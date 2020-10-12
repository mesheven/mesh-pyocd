"""
 mbed CMSIS-DAP debugger
 Copyright (c) 2006-2013 ARM Limited

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

from ...flash.flash import Flash
from ...coresight.coresight_target import CoreSightTarget
from ...core.memory_map import (FlashRegion, RamRegion, MemoryMap)
from ...debug.svd.loader import SVDFile
import logging


FLASH_ALGO = { 'load_address' : 0x10000000,
               'instructions' : [
                                  0xE00ABE00, 0x062D780D, 0x24084068, 0xD3000040, 0x1E644058, 0x1C49D1FA, 0x2A001E52, 0x4770D1F2,
                                  
                                  0x47700b00, 0x2200483b, 0x21016302, 0x63426341, 0x63816341, 0x20024937, 0x70083940, 0x47704610,
                                  0x47702000, 0xb08bb5f0, 0x25002032, 0x466a260f, 0xa905c261, 0x460f4c30, 0x47a04668, 0x28009805,
                                  0x2034d10a, 0xc1614669, 0x9003482c, 0x46684639, 0x980547a0, 0xd0002800, 0xb00b2001, 0xb570bdf0,
                                  0x0b04b08a, 0xa9052032, 0x4d239000, 0x460e9401, 0x46689402, 0x980547a8, 0xd10b2800, 0x90002034,
                                  0x9003481e, 0x94029401, 0x46684631, 0x980547a8, 0xd0002800, 0xb00a2001, 0xb5f0bd70, 0x0b004604,
                                  0x460eb08b, 0x91002132, 0x90029001, 0x4f12a905, 0x46684615, 0x47b8910a, 0x28009805, 0x2033d117,
                                  0x02360a36, 0xc1714669, 0x9004480c, 0x990a4668, 0x980547b8, 0xd10a2800, 0x46692038, 0x4807c171,
                                  0x46689004, 0x47b8990a, 0x28009805, 0x2001d0b5, 0x0000e7b3, 0x40048040, 0x1fff1ff1, 0x00002ee0,
                                  0x00000000,
                                ],
               'pc_init'          : 0x10000025,
               'pc_eraseAll'      : 0x10000045,
               'pc_erase_sector'  : 0x1000007F,
               'pc_program_page'  : 0x100000BB,
               'static_base'      : 0x10000120,
               'begin_data'       : 0x10000400, # Analyzer uses a max of 1 KB data (256 pages * 4 bytes / page)
               # disable double buffering, no enought RAM
               'begin_stack'      : 0x10001800,
               'min_program_length' : 256,
               'analyzer_supported' : True,
               'analyzer_address' : 0x10001800 # Analyzer 0x10001800..0x10001E00
              };


class LPC11U35(CoreSightTarget):

    VENDOR = "NXP"
    
    MEMORY_MAP = MemoryMap(
        FlashRegion(    start=0x00000000,  length=0x00010000,      blocksize=0x1000, is_boot_memory=True,
            algo=FLASH_ALGO),
        RamRegion(name='sram1',   start=0x10000000, length=0x2000),
        RamRegion(name='sram2',   start=0x20000000, length=0x0800)
        )

    def __init__(self, link):
        super(LPC11U35, self).__init__(link, self.MEMORY_MAP)
        self._svd_location = SVDFile.from_builtin("LPC11Uxx_v7.svd")

    def reset_stop_on_reset(self, software_reset=None, map_to_user=True):
        super(LPC11U35, self).reset_stop_on_reset(software_reset)

        # Remap to use flash and set SP and SP accordingly
        if map_to_user:
            self.write_memory(0x40048000, 0x2, 32)
            sp = self.read_memory(0x0)
            pc = self.read_memory(0x4)
            self.write_core_register('sp', sp)
            self.write_core_register('pc', pc)




