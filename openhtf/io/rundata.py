# Copyright 2014 Google Inc. All Rights Reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Parse and create OpenHTF run data.

Format:
  OpenHTF run data is in the JSON format and specifies the basic information
  about a running OpenHTF instance.

  {
    station_id: string,
    script_name: string,
    http_port: number,
    http_host: string,  // Always localhost
    pid: number,
  }

Convention:
  These files should be put into the /var/run/openhtf directory and named
  the station name of the running OpenHTF instance.  If an instance cannot
  be contacted by a reader of these files they're not allowed to remove them;
  instead, the recomendation is to check back periodically to see if
  they've been updated or to just recheck the instance later.
"""

import collections
import os
import json

import gflags


FLAGS = gflags.FLAGS
gflags.DEFINE_string('rundir', '/var/run/openhtf', 'Directory for runfiles.')



class RunData(collections.namedtuple(
    'RunData', ['station_id', 'script_name',
                'http_host', 'http_port', 'pid'])):
  """Encapsulates the run data stored in an openhtf file."""

  @classmethod
  def FromFile(cls, filename):
    """Creates RunData from a run file."""
    with open(filename) as runfile:
      data = runfile.read()
    decoded = json.loads(data)
    return cls(**decoded)

  def SaveToFile(self, directory):
    """Saves this run data to a file, typically in /var/run/openhtf.

    Args:
      directory: The directory in which to save this file.
    Return:
      The filename of this rundata.
    """
    filename = os.path.join(directory, self.station_id)
    with open(filename, 'w') as runfile:
      runfile.write(self.AsJSON())
    return filename

  def AsJSON(self):
    """Converts this run data instance to JSON."""
    data = self._asdict()
    data['http_host'] = self.http_host
    return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

  def IsAlive(self):
    """Returns True if this pid is alive."""
    try:
      os.kill(self.pid, 0)
    except OSError:
      return False
    else:
      return True


def EnumerateRunDirectory(directory):  # pylint: disable=invalid-name
  """Enumerates a local run directory to find stations.

  Args:
    directory: The directory to enumerate, we only list
               files in this directory no child directories.
  """
  filenames = os.listdir(directory)
  filepaths = [os.path.join(directory, filename) for filename in filenames]
  result = [RunData.FromFile(filepath) for filepath in filepaths if (
      os.path.isfile(filepath))]
  return result
