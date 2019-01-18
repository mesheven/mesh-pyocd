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

from ..flash.flash import Flash
from ..core.coresight_target import (SVDFile, CoreSightTarget)
from ..core.memory_map import (FlashRegion, RamRegion, MemoryMap)
import logging


DBGMCU_CR      = 0xE0042004
DBGMCU_APB1_CR = 0xE0042008
DBGMCU_APB2_CR = 0xE004200C

#0000 0000 0000 0000 0000 0000 0000 0000
DBGMCU_VAL      = 0x00000000
#0100 0010 0110 0000 0001 1100 0001 0001
DBGMCU_APB1_VAL = 0x42601C11

#0000 0000 0000 0000 0000 0000 0001 1101
DBGMCU_APB2_VAL = 0x0000001D


FLASH_ALGO = { 'load_address' : 0x20000000,
               'instructions' : [
                                  0xE00ABE00, 0x062D780D, 0x24084068, 0xD3000040, 0x1E644058, 0x1C49D1FA, 0x2A001E52, 0x4770D1F2,
                                  0x49554854, 0x48556048, 0x20006048, 0xb5104770, 0x20344603, 0x60e04c50, 0xbd102000, 0x20004601, 
                                  0xb5004770, 0x23002200, 0x6902484b, 0x0080f002, 0xd1012880, 0xffe4f7ff, 0x4847bf00, 0xf00368c3, 
                                  0x28000001, 0x4844d1f9, 0xf0426902, 0x61020204, 0xf0426902, 0x61020240, 0x483fbf00, 0xf00368c3, 
                                  0x28000001, 0x483cd1f9, 0xf0226902, 0x61020204, 0xbd002000, 0x4603b510, 0x24002200, 0x69024836, 
                                  0x0080f002, 0xd1012880, 0xffbaf7ff, 0x4832bf00, 0xf00468c4, 0x28000001, 0x482fd1f9, 0xf0426902, 
                                  0x61020202, 0x69026143, 0x0240f042, 0xbf006102, 0x68c44829, 0x0001f004, 0xd1f92800, 0x69024826, 
                                  0x0202f022, 0x20006102, 0xe92dbd10, 0x460545f0, 0x4617460e, 0x46902200, 0x462b4692, 0x481e463c, 
                                  0xf0026902, 0x28800080, 0xf7ffd101, 0xbf00ff89, 0xf8d04819, 0xf008800c, 0x28000001, 0xe01ed1f8, 
                                  0x69024815, 0x0201f042, 0x88206102, 0xbf008018, 0xf8d04811, 0xf008800c, 0x28000001, 0x8820d1f8, 
                                  0x42888819, 0x480cd007, 0xf0226902, 0x61020201, 0xe8bd2001, 0x1c9b85f0, 0xf10a1ca4, 0xebba0a01, 
                                  0xd3dd0f56, 0x69024804, 0x0201f022, 0x20006102, 0x0000e7ef, 0x45670123, 0x40022000, 0xcdef89ab, 
                                  0x00000000,
                                ],
               'pc_init'          : 0x2000002F,
               'pc_eraseAll'      : 0x20000043,
               'pc_erase_sector'  : 0x20000095,
               'pc_program_page'  : 0x200000EB,
               'static_base'      : 0x200001A4,
               'begin_data'       : 0x20000400, # Analyzer uses a max of 256 B data (64 pages * 4 bytes / page)
               'page_buffers'     : [0x20000400, 0x20000C00],   # Enable double buffering
               'begin_stack'      : 0x20001400,
               'min_program_length' : 2,
               'analyzer_supported' : True,
               'analyzer_address' : 0x20001800 # Analyzer 0x20001800..0x20001C00
              };


class STM32F301K8(CoreSightTarget):

    memoryMap = MemoryMap(
        FlashRegion(    start=0x08000000,  length=0x10000,      blocksize=0x800, is_boot_memory=True,
            algo=FLASH_ALGO),
        RamRegion(      start=0x20000000,  length=0x4000)
        )

    def __init__(self, link):
        super(STM32F301K8, self).__init__(link, self.memoryMap)
        self._svd_location = SVDFile(vendor="STMicro", filename="STM32F0xx.svd", is_local=False)

    def create_init_sequence(self):
        seq = super(STM32F301K8, self).create_init_sequence()

        seq.insert_after('create_cores',
            ('setup_dbgmcu', self.setup_dbgmcu)
            )

        return seq
        
    def setup_dbgmcu(self):
        logging.debug('stm32f301k8 init')
        self.write_memory(DBGMCU_CR, DBGMCU_VAL)
        self.write_memory(DBGMCU_APB1_CR, DBGMCU_APB1_VAL)
        self.write_memory(DBGMCU_APB2_CR, DBGMCU_APB2_VAL)
