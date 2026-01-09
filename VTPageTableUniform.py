import struct
from dataclasses import dataclass
from typing import Tuple, List

@dataclass
class VTPageTableUniform:
    """Unpacked contents of per page table uniforms."""
    XOffsetInPages: int = 0      # 12 bits
    YOffsetInPages: int = 0      # 12 bits
    MaxLevel: int = 0            # 4 bits
    vPageTableMipBias: int = 0   # 4 bits
    MipBiasGroup: int = 0        # 2 bits
    ShiftedPageTableID: int = 0  # 4 bits
    AdaptiveLevelBias: int = 0   # 4 bits
    
    SizeInPages: Tuple[float, float] = (0.0, 0.0)
    UVScale: Tuple[float, float] = (0.0, 0.0)
    MaxAnisoLog2: float = 0.0
    
    def __str__(self):
        return f"""VTPageTableUniform:
  UVScale:            ({self.UVScale[0]:.6f}, {self.UVScale[1]:.6f})
  SizeInPages:        ({self.SizeInPages[0]:.6f}, {self.SizeInPages[1]:.6f})
  MaxAnisoLog2:       {self.MaxAnisoLog2:.6f}
  XOffsetInPages:     {self.XOffsetInPages} (0x{self.XOffsetInPages:03X})
  YOffsetInPages:     {self.YOffsetInPages} (0x{self.YOffsetInPages:03X})
  vPageTableMipBias:  {self.vPageTableMipBias}
  MipBiasGroup:       {self.MipBiasGroup}
  MaxLevel:           {self.MaxLevel}
  AdaptiveLevelBias:  {self.AdaptiveLevelBias}
  ShiftedPageTableID: {self.ShiftedPageTableID} (0x{self.ShiftedPageTableID:08X})
"""


def uint_to_float(u: int) -> float:
    """asfloat equivalent: reinterpret uint32 bits as float32"""
    return struct.unpack('f', struct.pack('I', u & 0xFFFFFFFF))[0]


def VTPageTableUniform_Unpack_uint4x2(
    PackedPageTableUniform0: Tuple[int, int, int, int],
    PackedPageTableUniform1: Tuple[int, int, int, int]
) -> VTPageTableUniform:
    """
    从两个 uint4 解包 (完整版本)
    PackedPageTableUniform0: (x, y, z, w) - uint4
    PackedPageTableUniform1: (x, y, z, w) - uint4
    """
    result = VTPageTableUniform()
    
    # PackedPageTableUniform0.xy -> UVScale (as float)
    # PackedPageTableUniform0.zw -> SizeInPages (as float)
    result.UVScale = (
        uint_to_float(PackedPageTableUniform0[0]),
        uint_to_float(PackedPageTableUniform0[1])
    )
    result.SizeInPages = (
        uint_to_float(PackedPageTableUniform0[2]),
        uint_to_float(PackedPageTableUniform0[3])
    )
    
    # PackedPageTableUniform1.x -> MaxAnisoLog2 (as float)
    result.MaxAnisoLog2 = uint_to_float(PackedPageTableUniform1[0])
    
    # PackedPageTableUniform1.y 解包多个字段
    packed_y = PackedPageTableUniform1[1]
    result.XOffsetInPages = packed_y & 0xFFF                    # bits [0:11]
    result.YOffsetInPages = (packed_y >> 12) & 0xFFF            # bits [12:23]
    result.vPageTableMipBias = (packed_y >> 24) & 0xF           # bits [24:27]
    result.MipBiasGroup = (packed_y >> 28) & 0x3                # bits [28:29]
    
    # PackedPageTableUniform1.z 解包
    packed_z = PackedPageTableUniform1[2]
    result.MaxLevel = packed_z & 0xF                            # bits [0:3]
    result.AdaptiveLevelBias = (packed_z >> 4) & 0xF            # bits [4:7]
    
    # PackedPageTableUniform1.w -> ShiftedPageTableID
    result.ShiftedPageTableID = PackedPageTableUniform1[3]
    
    return result


def VTPageTableUniform_Unpack_uint2(
    PackedPageTableUniform: Tuple[int, int]
) -> VTPageTableUniform:
    """
    从一个 uint2 解包 (简化版本)
    PackedPageTableUniform: (x, y) - uint2
    """
    result = VTPageTableUniform()
    
    result.UVScale = (1.0, 1.0)
    result.MaxAnisoLog2 = 0.0
    result.MipBiasGroup = 0
    result.AdaptiveLevelBias = 0
    
    packed_x = PackedPageTableUniform[0]
    packed_y = PackedPageTableUniform[1]
    
    # 从 packed_y 解包 SizeInPages
    result.SizeInPages = (
        float(packed_y & 0xFFF),
        float((packed_y >> 12) & 0xFFF)
    )
    
    # 从 packed_x 解包
    result.XOffsetInPages = packed_x & 0xFFF
    result.YOffsetInPages = (packed_x >> 12) & 0xFFF
    result.vPageTableMipBias = (packed_x >> 24) & 0xF
    result.MaxLevel = (packed_y >> 24) & 0xF
    result.ShiftedPageTableID = packed_x & 0xF0000000
    
    return result


# ============================================================
# 使用示例
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("VT PageTable Uniform 解包工具")
    print("=" * 60)
    
    # 示例1: 使用 uint4 x 2 格式
    # 从 RenderDoc 截帧获取的值，填入这里
    # Material_VTPackedPageTableUniform[0] 和 [1]
    packed0 = (0x00000000, 0x00001000, 0x00000004, 0x00000000)  # 示例值
    packed1 = (0x00000000, 0x00001000, 0x00000004, 0x00000000)  # 示例值
    
    print("\n【uint4 x 2 格式解包】")
    print(f"PackedPageTableUniform0: {tuple(hex(x) for x in packed0)}")
    print(f"PackedPageTableUniform1: {tuple(hex(x) for x in packed1)}")
    result1 = VTPageTableUniform_Unpack_uint4x2(packed0, packed1)
    print(result1)
    
    # ============================================================
    # 实际使用: 替换下面的值为你从 RenderDoc 截取的实际数据
    # ============================================================
    
    print("\n" + "=" * 60)
    print("【请替换为你的实际数据】")
    print("=" * 60)
    
    # VTStack[0]: VS 中使用 (WPO)
    # Material_VTPackedPageTableUniform[0]
    vs_packed0 = (1065353216, 1065353216, 1090519040, 1090519040)
    # Material_VTPackedPageTableUniform[1]
    vs_packed1 = (1077936128, 117440528, 3, 268435456)
    
    # VTStack[1]: PS 中使用 (BaseColor)
    # Material_VTPackedPageTableUniform[2]
    ps_packed0 = (1065353216, 1065353216, 1090519040, 1090519040)
    # Material_VTPackedPageTableUniform[3]
    ps_packed1 = (1077936128, 117440520, 3, 0)

    
    print("\n【VS (WPO) - VTStack[0]】")
    vs_result = VTPageTableUniform_Unpack_uint4x2(vs_packed0, vs_packed1)
    print(vs_result)
    
    print("\n【PS (BaseColor) - VTStack[1]】")
    ps_result = VTPageTableUniform_Unpack_uint4x2(ps_packed0, ps_packed1)
    print(ps_result)
    
    # 比较差异
    print("\n" + "=" * 60)
    print("【VS vs PS 差异对比】")
    print("=" * 60)
    
    def compare_fields(vs: VTPageTableUniform, ps: VTPageTableUniform):
        fields = [
            'UVScale', 'SizeInPages', 'MaxAnisoLog2',
            'XOffsetInPages', 'YOffsetInPages', 'vPageTableMipBias',
            'MipBiasGroup', 'MaxLevel', 'AdaptiveLevelBias', 'ShiftedPageTableID'
        ]
        for field in fields:
            vs_val = getattr(vs, field)
            ps_val = getattr(ps, field)
            match = "✓" if vs_val == ps_val else "✗ DIFFERENT"
            print(f"  {field:20s}: VS={vs_val}, PS={ps_val}  {match}")
    
    compare_fields(vs_result, ps_result)