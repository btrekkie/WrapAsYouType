# Stripped-down implementation of functools.lru_cache.  This exists for
# compatability with Python 2.  The implementation is adapted from
# https://raw.githubusercontent.com/python/cpython/3.7/Lib/functools.py .

from collections import namedtuple
from functools import update_wrapper


################################################################################
### LRU Cache function decorator
################################################################################

_CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "maxsize", "currsize"])

class _HashedSeq(list):
    """ This class guarantees that hash() will be called no more than once
        per element.  This is important because the lru_cache() will hash
        the key multiple times on a cache miss.

    """

    __slots__ = 'hashvalue'

    def __init__(self, tup, hash=hash):
        self[:] = tup
        self.hashvalue = hash(tup)

    def __hash__(self):
        return self.hashvalue

def _make_key(args, kwds, typed,
             kwd_mark = (object(),),
             fasttypes = set([int, str, frozenset, type(None)]),
             tuple=tuple, type=type, len=len):
    """Make a cache key from optionally typed positional and keyword arguments

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    """
    # All of code below relies on kwds preserving the order input by the user.
    # Formerly, we sorted() the kwds before looping.  The new way is *much*
    # faster; however, it means that f(x=1, y=2) will now be treated as a
    # distinct call from f(y=2, x=1) which will be cached separately.
    key = args
    if kwds:
        key += kwd_mark
        for item in kwds.items():
            key += item
    if typed:
        key += tuple(type(v) for v in args)
        if kwds:
            key += tuple(type(v) for v in kwds.values())
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedSeq(key)

def lru_cache(maxsize=128, typed=False):
    """Least-recently-used cache decorator.

    If *maxsize* is set to None, the LRU features are disabled and the cache
    can grow without bound.

    If *typed* is True, arguments of different types will be cached separately.
    For example, f(3.0) and f(3) will be treated as distinct calls with
    distinct results.

    Arguments to the cached function must be hashable.

    View the cache statistics named tuple (hits, misses, maxsize, currsize)
    with f.cache_info().  Clear the cache and statistics with f.cache_clear().
    Access the underlying function with f.__wrapped__.

    See:  http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used

    """

    # Users should only access the lru_cache through its public API:
    #       cache_info, cache_clear, and f.__wrapped__
    # The internals of the lru_cache are encapsulated for thread safety and
    # to allow the implementation to change (including a possible C version).

    # Early detection of an erroneous call to @lru_cache without any arguments
    # resulting in the inner function being passed to maxsize instead of an
    # integer or None.
    if maxsize is not None and not isinstance(maxsize, int):
        raise TypeError('Expected maxsize to be an integer or None')

    def decorating_function(user_function):
        wrapper = _lru_cache_wrapper(user_function, maxsize, typed, _CacheInfo)
        return update_wrapper(wrapper, user_function)

    return decorating_function

def _lru_cache_wrapper(user_function, maxsize, typed, _CacheInfo):
    # Constants shared by all lru cache instances:
    make_key = _make_key         # build a key from the function arguments
    PREV, NEXT, KEY, RESULT = 0, 1, 2, 3   # names for the link fields

    cache = {}
    cache_get = cache.get    # bound method to lookup a key or return None
    cache_len = cache.__len__  # get cache size without calling len()
    root = []                # root of the circular doubly linked list
    root[:] = [root, root, None, None]     # initialize by pointing to self
    
    # Python 2 does not support the keyword "nonlocal".  To enable "wrapper" to
    # alter the values it uses for "root" and "full" in a manner compatible
    # with Python 2, we wrap them in one-element arrays.
    full_ref = [False]
    root_ref = [root]

    def wrapper(*args, **kwds):
        # Size limited caching that tracks accesses by recency
        root = root_ref[0]
        key = make_key(args, kwds, typed)
        link = cache_get(key)
        if link is not None:
            # Move the link to the front of the circular queue
            link_prev, link_next, _key, result = link
            link_prev[NEXT] = link_next
            link_next[PREV] = link_prev
            last = root[PREV]
            last[NEXT] = root[PREV] = link
            link[PREV] = last
            link[NEXT] = root
            return result
        result = user_function(*args, **kwds)
        if full_ref[0]:
            # Use the old root to store the new key and result.
            oldroot = root
            oldroot[KEY] = key
            oldroot[RESULT] = result
            # Empty the oldest link and make it the new root.
            # Keep a reference to the old key and old result to
            # prevent their ref counts from going to zero during the
            # update. That will prevent potentially arbitrary object
            # clean-up code (i.e. __del__) from running while we're
            # still adjusting the links.
            root = oldroot[NEXT]
            root_ref[0] = root
            oldkey = root[KEY]
            root[KEY] = root[RESULT] = None
            # Now update the cache dictionary.
            del cache[oldkey]
            # Save the potentially reentrant cache[key] assignment
            # for last, after the root and links have been put in
            # a consistent state.
            cache[key] = oldroot
        else:
            # Put result in a new link at the front of the queue.
            last = root[PREV]
            link = [last, root, key, result]
            last[NEXT] = root[PREV] = cache[key] = link
            # Use the cache_len bound method instead of the len() function
            # which could potentially be wrapped in an lru_cache itself.
            full_ref[0] = (cache_len() >= maxsize)
        return result

    return wrapper
