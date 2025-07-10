"""PokeWalker Course Injector"""
from dataclasses import dataclass
from typing import List
import os
from pokemonenums import RouteImage, Species, Move, Gender, Type, ITEMS

def read_binary(filename: str):
    """Read binary file as bytearray"""
    with open(filename, "rb") as file:
        return bytearray(file.read())

# Make DEFAULT_DATA optional - only load if file exists
def get_default_data():
    """Get default data if file exists, otherwise return empty bytearray"""
    try:
        # Try to find the file in the same directory as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        default_file = os.path.join(script_dir, "default_courses.bin")
        if os.path.exists(default_file):
            return read_binary(default_file)
        else:
            return bytearray()
    except:
        return bytearray()

DEFAULT_DATA = get_default_data()
DATA_OFFSET = 0x21F4138

@dataclass
class PokeWalkerSlot:
    """PokeWalker Pokemon"""
    species: Species
    level: int
    item: str
    form: int
    gender: Gender
    moves: List[Move]
    step_requirement: int
    rarity_weight: int

    def to_bytes(self) -> bytearray:
        """Convert PokeWalkerSlot to bytearray"""
        data = bytearray()
        data += int(self.species.value).to_bytes(2, 'little')
        data += self.level.to_bytes(2, 'little')
        data += ITEMS.index(self.item).to_bytes(2, 'little')
        data += self.form.to_bytes(1, 'little')
        
        # Combine gender and form into one byte
        # Based on source code analysis:
        # - Bits 0-4: Gender (0-31)
        # - Bits 5-6: Form (0-3) 
        gender_form_byte = int(self.gender.value) & 0x1F  # Lower 5 bits for gender
        gender_form_byte |= (self.form & 0x03) << 5      # Bits 5-6 for form
        data += gender_form_byte.to_bytes(1, 'little')
        
        for move in self.moves:
            data += int(move.value).to_bytes(2, 'little')
        data += self.step_requirement.to_bytes(2, 'little')
        data += self.rarity_weight.to_bytes(2, 'little')
        return data

@dataclass
class PokeWalkerItem:
    """PokeWalker Item"""
    item: str
    step_requirement: int
    rarity_weight: int

    def to_bytes(self) -> bytearray:
        """Convert PokeWalkerItem to bytearray"""
        data = bytearray()
        data += ITEMS.index(self.item).to_bytes(2, 'little')
        data += self.step_requirement.to_bytes(2, 'little')
        data += self.rarity_weight.to_bytes(2, 'little')
        return data

@dataclass
class PokeWalkerCourse:
    """PokeWalker Course Data"""
    watt_requirement: int
    route_image: RouteImage
    group_a: List[PokeWalkerSlot]
    group_b: List[PokeWalkerSlot]
    group_c: List[PokeWalkerSlot]
    items: List[PokeWalkerItem]
    special_types: List[Type]

    def to_bytes(self) -> bytearray:
        """Convert PokeWalkerCourse to bytearray"""
        if not 0 <= self.watt_requirement < 2 ** 32:
            raise Exception("Watt requirement must be a 32-bit unsigned integer")
        if len(self.group_a) != 2 or len(self.group_b) != 2 or len(self.group_c) != 2:
            raise Exception("All groups must contain 2 pokemon")
        if len(self.items) != 10:
            raise Exception("10 items are required")
        if len(self.special_types) != 3:
            raise Exception("3 special types are required")
        data = bytearray()
        data += self.watt_requirement.to_bytes(4, 'little')
        data += int(self.route_image.value).to_bytes(4, 'little')
        for slot in self.group_a:
            data += slot.to_bytes()
        for slot in self.group_b:
            data += slot.to_bytes()
        for slot in self.group_c:
            data += slot.to_bytes()
        for item in self.items:
            data += item.to_bytes()
        for special_type in self.special_types:
            data += int(special_type.value).to_bytes(1, 'little')
        data += (0).to_bytes(1, 'little')
        return data

    def to_ar_code(self) -> str:
        """Convert PokeWalkerCourse to AR code"""
        data = self.to_bytes()
        code = "94000130 FCFF0000\n" # L+R to trigger
        for offset in range(0,len(data),4):
            code += f"{DATA_OFFSET + offset:08X} " \
                    f"{int.from_bytes(data[offset:offset + 4], 'little'):08X}\n"
        return code

    def to_usr_cheat_dat(self) -> bytearray:
        """Convert PokeWalkerCourse to usrcheat.dat"""
        database_title_text = "PokeWalker"
        # USA HeartGold
        game_id_text = "IPKE"
        game_id_value = 0x4DFFBF91
        game_title_text = "USA HeartGold"
        # # USA SoulSilver
        # game_id_text = "IPGE"
        # game_id_value = 0x2D5118CA
        # game_title_text = "USA SoulSilver"
        code_title_text = "Custom PokeWalker Course"
        code_text = self.to_ar_code()

        header = b"R4 CheatCode"
        header += bytearray.fromhex("00 01 00 00")

        name = database_title_text.encode("utf-8")
        name += bytearray.fromhex("00") * (0x3B - len(name))
        name += bytearray.fromhex("00 D5 53 41 59")

        filler = bytearray.fromhex("01") + bytearray.fromhex("00") * 0xAF

        game_id = game_id_text.encode("utf-8") + game_id_value.to_bytes(4, 'little')
        game_id += bytearray.fromhex("20 01") + bytearray.fromhex("00") * 0x16

        game_title = game_title_text.encode("utf-8")
        game_title += ((((len(game_title) // 4) + 1) * 4) - len(game_title)) \
            * bytearray.fromhex("00") \
            + bytearray.fromhex("01") \
            + 7 * bytearray.fromhex("00") \
            + bytearray.fromhex("01") \
            + 0x1b * bytearray.fromhex("00")

        code_title = code_title_text.encode("utf-8")
        code_title_len_mod = len(code_title) % 4
        if code_title_len_mod >= 3:
            code_title_len_mod -= 4
        code_title += bytearray.fromhex("00") * ((4 - code_title_len_mod))

        code_data = b''.join([int(x,16).to_bytes(4,'little') for x in code_text.split()])
        code_data = (len(code_data) // 4).to_bytes(4, 'little') + code_data

        code = code_title + code_data
        code = (len(code) // 4).to_bytes(4, 'little') + code

        return header + name + filler + game_id + game_title + code

arceus = PokeWalkerSlot(
    species=Species.ARCEUS,
    level=50,
    item="None",
    form=0,
    gender=Gender.GENDERLESS,
    moves=[Move.JUDGMENT, Move.EXTREMESPEED, Move.SWORDSDANCE, Move.RECOVER],
    step_requirement=0,
    rarity_weight=33,
)

master_ball = PokeWalkerItem(
    item="Master Ball",
    step_requirement=0,
    rarity_weight=10,
)

# Example usage (commented out to avoid file operations at import time)
# course = PokeWalkerCourse(
#     watt_requirement=0,
#     route_image=RouteImage.VOLCANO,
#     group_a=[arceus] * 2,
#     group_b=[arceus] * 2,
#     group_c=[arceus] * 2,
#     items=[master_ball] * 10,
#     special_types=[Type.FIRE, Type.WATER, Type.GRASS]
# )

# with open("usrcheat.dat", "wb+") as usrcheat:
#     usrcheat.write(course.to_usr_cheat_dat())
