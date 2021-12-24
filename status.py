"""
Simple daemon that prints out
the current appplication that is using the webcam
"""
import winreg as wr
import time

LAST_USED_TIME_STOP = "LastUsedTimeStop"
CAM_KEY = r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam"
MIC_KEY = r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone"


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
    
    result = []
    for i in range(num_subkeys):
        subkey_name = wr.EnumKey(key, i)
        with wr.OpenKey(key, subkey_name) as subkey:
            if subkey_name == "NonPackaged":
                sub_result = iterate_middle_node(subkey)
                result.extend(sub_result)
            else:
                sub_result = iterate_leaf(subkey)
                if sub_result:
                    result.append(subkey_name)

    return result


def check_status():
    """
    Returns the names of the applications that are using the webcam,
    and the names of the applications that are using the microphone.
    """
    registry = wr.ConnectRegistry(None, wr.HKEY_CURRENT_USER)
    with wr.OpenKey(registry, CAM_KEY) as key:
        camera = iterate_middle_node(key)
    with wr.OpenKey(registry, MIC_KEY) as key:
        microphone = iterate_middle_node(key)
        
    return (camera,microphone)


if __name__ == "__main__":

    while True:
        print(check_status())
        time.sleep(0.5)
