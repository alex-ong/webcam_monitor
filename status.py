"""
Simple daemon that prints out
the current appplication that is using the webcam
"""
import winreg as wr
import time

LAST_USED_TIME_STOP = "LastUsedTimeStop"
ROOT_KEY = r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam"


def iterate_leaf(key):
    """
    Iterates leaf node (this thing should contain LastUsedTimeStart and LastUsedTimeStop)
    Returns true it ocntains LastUsedTimeStop and its value is 0x00000000,
    As this indicates that a camera is in use.
    """
    _, num_subvalues, __ = wr.QueryInfoKey(key)
    for i in range(num_subvalues):
        name, value, _ = wr.EnumValue(key, i)
        if name == LAST_USED_TIME_STOP and value == 0:
            return True

    return False


def iterate_middle_node(key):
    """
    Recursively iterates a non-leaf node.
    Returns name of application currently accessing the webcam.
    """
    num_subkeys, _, __ = wr.QueryInfoKey(key)

    for i in range(num_subkeys):
        subkey_name = wr.EnumKey(key, i)
        with wr.OpenKey(key, subkey_name) as subkey:
            if subkey_name == "NonPackaged":
                sub_result = iterate_middle_node(subkey)
                if sub_result is not None:
                    return sub_result
            else:
                sub_result = iterate_leaf(subkey)
                if sub_result:
                    return subkey_name

    return None


def iterate_main():
    """
    Returns the name of the application that is using the webcam,
    or None if it is not in use.
    """
    registry= wr.ConnectRegistry(None, wr.HKEY_CURRENT_USER)
    with wr.OpenKey(registry, ROOT_KEY) as key:
        result = iterate_middle_node(key)
    return result


if __name__ == "__main__":

    while True:
        print(iterate_main())
        time.sleep(0.5)
