################################
# Driftwood 2D Game Dev. Suite #
# check.py                     #
# Copyright 2014-2017          #
# Sei Satzparad & Paul Merrill #
################################

# **********
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# **********

from typing import Any, Union, List


class CheckFailure(Exception):
    """This exception is raised when a CHECK() fails.

    This only needs to exist. It belongs to the global scope so it's recognized anywhere.
    """

    # Do nothing.


def CHECK(
    item: Any, _type: Union[type, List[type]], _min: float = None, _max: float = None, _equals: float = None
) -> bool:
    """Check if an input matches type, min, max, and/or equality requirements.

    This function belongs to the global scope as CHECK().

    For integers and floats, the min, max, and equals checks work as one would expect. For strings, lists, and
    tuples, they compare length. For dicts they compare numbers of keys.

    On failure, a CheckFailure will be raised. CheckFailure belongs to the global scope so all scripts
    know what it is.

    The correct way to use CHECK()s is to wrap them in a try/except clause and then catch CheckFailure. When
    caught, the text contents of the exception can be logged to give more information.

    Arguments:
        item: Input to be checked.
        _type: The type the input is expected to be. Can be a single type or a list of types.
        _min: If set, the minimum value, length, or size of the input, depending on type.
        _max: If set, the maximum value, length, or size of the input, depending on type.
        _equals: If set, check if the value, length, or size of the input is equal to _equals, depending on type.

    Returns:
        True if succeeded, raises CheckFailure if failed, containing failure message.
    """
    # Check if we are trying to check min, max, or equality on an unsupported type.
    if type(item) not in [int, float, str, list, tuple, dict] and (
        _min is not None or _max is not None or _equals is not None
    ):
        raise CheckFailure("could not check input: cannot perform numeric checks on type {0}".format(type(item), _type))

    # Type check.
    if type(item) is not _type and (type(_type) is list and type(item) not in _type):
        raise CheckFailure("input failed type check: {0}: expected {1} instead".format(type(item), _type))

    # Minimum check.
    if _min is not None:
        if type(_min) not in [int, float]:
            # Bad argument.
            raise CheckFailure("could not check input: illegal type {0} for _min argument".format(type(_min)))
        if type(item) in [int, float]:
            # Check value.
            if item < _min:
                raise CheckFailure(
                    "input of type {0} failed min check: expected value >= {1}, got {2}".format(_type, _min, item)
                )
        elif type(item) in [str, list, tuple]:
            # Check length.
            if len(item) < _min:
                raise CheckFailure(
                    "input of type {0} failed min check: expected length >= {1}, got {2}".format(_type, _min, len(item))
                )
        elif type(item) in [dict]:
            # Check size.
            if len(item.keys()) < _min:
                raise CheckFailure(
                    "input of type {0}  failed min check: expected >= {1} keys, got {2}".format(
                        _type, _min, len(item.keys())
                    )
                )

    # Maximum check.
    if _max is not None:
        if type(_max) not in [int, float]:
            # Bad argument.
            raise CheckFailure("could not check input: illegal type {0} for _max argument".format(type(_max)))
        if type(item) in [int, float]:
            # Check value.
            if item > _max:
                raise CheckFailure(
                    "input of type {0}  failed max check: expected value <= {1}, got {2}".format(_type, _min, item)
                )
        elif type(item) in [str, list, tuple]:
            # Check length.
            if len(item) > _max:
                raise CheckFailure(
                    "input of type {0} failed max check: expected length <= {1}, got {2}".format(_type, _min, len(item))
                )
        elif type(item) in [dict]:
            # Check size.
            if len(item.keys()) > _max:
                raise CheckFailure(
                    "input of type {0} failed max check: expected <= {1} keys, got {2}".format(
                        _type, _min, len(item.keys())
                    )
                )

    # Equality check.
    if _equals is not None:
        if type(_equals) not in [int, float]:
            # Bad argument.
            raise CheckFailure("could not check input: illegal type {0} for _equals argument".format(type(_equals)))
        if type(item) in [int, float]:
            # Check value.
            if item is not _equals:
                raise CheckFailure(
                    "input of type {0} failed equality check: expected value == {1}, got {2}".format(_type, _min, item)
                )
        elif type(item) in [str, list, tuple]:
            # Check length.
            if len(item) is not _equals:
                raise CheckFailure(
                    "input of type {0} failed equality check: expected length == {1}, got {2}".format(
                        _type, _min, len(item)
                    )
                )
        elif type(item) in [dict]:
            # Check size.
            if len(item.keys()) is not _equals:
                raise CheckFailure(
                    "input of type {0} failed equality check: expected {1} keys, got {2}".format(
                        _type, _min, len(item.keys())
                    )
                )

    # Success.
    return True
