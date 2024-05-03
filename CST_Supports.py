import json
from pathlib import Path


class Parameters(object):
    """
    Container class for passing/tracking parameters.
    Can either subclass or add values at runtime.

    Parameters
    ----------
    None.

    Methods
    ----------
    get_these_values(): accepts a list of variables, and returns the values
                        of these variables as a list, or as a dictonary
    as_dict(): returns all parameter key/value pairs in dictionary
    as_str(): returns all parameter key/value pairs in formatted string
    print_values(): prints all parameter key/value pairs to screen

    """

    def __init__(self):
        """Put your parameters and initial values here."""
        self.param_desc = "Parameters"

    def __max_str_len(self):
        maxlen = 0
        for k in self.__dict__.keys():
            tmp_len = len(k)
            if tmp_len > maxlen:
                maxlen = tmp_len
        return maxlen

    def as_str(self):
        """Return key/value pairs in a formatted string"""
        param_str = ""
        msl = self.__max_str_len()
        for k in self.__dict__.keys():
            if "__" not in k:
                param_str += f"{str(k):{msl}}:  {self.__dict__[k]}\n"
        return param_str

    def get_these_values(self, get_list, as_list=True):
        """
        Return specific param values in 'get_list'.
        If 'as_list' is True, return as list.
        Otherwise, you get them as a dictionary.
        Those are your choices. :)
        """
        L = [self.__dict__[k] for k in get_list if k in self.__dict__.keys()]

        if as_list is True:
            return L
        else:
            return dict(zip(get_list, L))

    def as_dict(self):
        """Return key/value pairs in a dictionary."""
        d = {k: self.__dict__[k] for k in self.__dict__.keys() if "__" not in k}
        return d

    def load_parameters(self, dict_path):
        with open(dict_path, "r") as f:
            res = f.read()
        js = json.loads(res)
        self.__dict__.update(js)

    def print_values(self):
        """Print key/value pairs to stdio."""
        param_str = self.as_str()
        print(f"\n{self.param_desc}:\n{param_str}")

    def update_dict(self, updated_dict):
        self.__dict__.update(updated_dict)

    def save_as_json(self, file_path):
        """Save Parameters to file_path."""
        with open(file_path, "w") as f:
            json.dump(self.as_dict(), f)


class legacy_Parameters(object):
    """
    Container class for passing/tracking parameters.
    Can either subclass to set paramater values or
    add values at runtime.

    Parameters
    ----------
    None.

    Methods
    ----------
    get_these_values(): accepts a list of variables, and returns the values
                        of these variables as a list, or as a dictonary
    as_dict(): returns all parameter key/value pairs in dictionary
    as_str(): returns all parameter key/value pairs in formatted string
    print_values(): prints all parameter key/value pairs to screen

    """

    def __init__(self):
        """Put your parameters and initial values here."""
        self.param_desc = "Parameters"

    def __max_str_len(self):
        maxlen = 0
        for k in self.__dict__.keys():
            tmp_len = len(k)
            if tmp_len > maxlen:
                maxlen = tmp_len
        return maxlen

    def as_str(self):
        """Return key/value pairs in a formatted string"""
        param_str = ""
        msl = self.__max_str_len()
        for k in self.__dict__.keys():
            if "__" not in k:
                param_str += f"{str(k):{msl}}:  {self.__dict__[k]}\n"
        return param_str

    def get_these_values(self, get_list, as_list=True):
        """
        Return specific param values in 'get_list'.
        If 'as_list' is True, return as list.
        Otherwise, you get them as a dictionary.
        Those are your choices. :)
        """
        L = []
        for k in get_list:
            L.append(self.__dict__[k])
        if as_list is True:
            return L
        else:
            return dict(zip(get_list, L))

    def as_dict(self):
        """Return key/value pairs in a dictionary."""

        keys = [k for k in self.__dict__.keys() if "__" not in k]
        d = {}
        for k in keys:
            d[k] = self.__dict__[k]
        return d

    def print_values(self):
        """Print key/value pairs to stdio."""
        param_str = self.as_str()
        print(f"\n{self.param_desc}:\n{param_str}")


def safepath(dest_path):
    """
    Takes a string representation of a filepath. Returns a filename and
    location preserving the stem and extension of the original, but
    (possibly) modified by appending a zero-padded incremental index to
    the file stem. This ensures that a new file written to that location
    will not overwrite an existing file.

    Parameters
    ----------
    dest_path : string, required
            A filepath destination.

    Returns
    ----------
    safe_path : string
            A safe filepath.

    Example
    ----------
    Calling safepath("srt_timing.log") in a flder where that filepath exists
    will return "srt_timing_001.log".
    Calling safepath("srt_timing.log") again in that same folder will returns
    "srt_timing_002.log", and so on.
    """
    safe_path = None
    old_p = Path(dest_path)
    stem = old_p.stem
    ext = old_p.suffix

    if old_p.exists() is False:
        return dest_path
    else:
        cnt = 1
        p = Path(dest_path)
        while p.exists() is True:
            idx = f"{cnt:03}"
            safe_path = f"{stem}_{idx}{ext}"
            p = Path(safe_path)
            if cnt >= 1000:
                raise ValueError(
                    f"""
                Ran out of zero padded names.
                Current limit is: {cnt}.
                Consider deleting some of the files."""
                )
            cnt += 1
    return safe_path
