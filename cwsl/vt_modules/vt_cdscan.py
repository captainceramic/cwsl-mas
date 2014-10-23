"""

Wrapper for cdscan (CDAT) fo create a virtual aggregation catalogue file.

Part of the CWSLab VisTrails plugin.

Authors: Tim Bedin, Tim.Bedin@csiro.au
         Tim Erwin, Tim.Erwin@csiro.au

Copyright 2014 CSIRO

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


"""

import os

from vistrails.core.modules import vistrails_module
from vistrails.core.modules.basic_modules import String, List

from cwsl.configuration import configuration
from cwsl.core.constraint import Constraint
from cwsl.core.process_unit import ProcessUnit
from cwsl.core.pattern_generator import PatternGenerator


class CDScan(vistrails_module.Module):

    # Define the module ports.
    _input_ports = [('in_dataset', 'csiro.au.cwsl:VtDataSet'),
                    ('added_constraints', List, True,
                     {'defaults': ['[]']})]

    _output_ports = [('out_dataset', 'csiro.au.cwsl:VtDataSet'),
                     ('out_constraints', String)]

    _execution_options = {'required_modules': ['cdo', 'cct', 'nco',
                                               'python/2.7.5','python-cdat-lite/6.0rc2-py2.7.5']
                         }

    def __init__(self):

        super(CDScan, self).__init__()
 
        self.command = '${CWSL_CTOOLS}/aggregation/version_safe_cdscan.py'
        self.out_pattern = PatternGenerator('user', 'cdat_lite_catalogue').pattern

    def compute(self):

        in_dataset = self.getInputFromPort('in_dataset')
        try:
            # Add extra constraints if necessary.
            added_constraints = self.getInputFromPort('added_constraints')
        except vistrails_module.ModuleError:
            added_constraints = None

        # Change the file_type constraint from nc to xml and add
        # any added constraints.
        cons_for_output = set([Constraint('suffix', ['xml'])])
        if added_constraints:
            cons_for_output = set.union(cons_for_output,
                                        set(added_constraints))


        # Execute the xml_to_nc process.
        this_process = ProcessUnit([in_dataset],
                                   self.out_pattern,
                                   self.command,
                                   cons_for_output,
                                   execution_options=self._execution_options)

        this_process.execute(simulate=configuration.simulate_execution)
        process_output = this_process.file_creator

        self.setResult('out_dataset', process_output)
        self.setResult('out_constraints', str(process_output.constraints))
