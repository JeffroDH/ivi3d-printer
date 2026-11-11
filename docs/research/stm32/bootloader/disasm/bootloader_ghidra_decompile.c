// ===== thunk_FUN_08005b4c @ 08000190

void thunk_FUN_08005b4c(void)

{
  (*DAT_08000194)();
  return;
}


// ===== FUN_0800019c @ 0800019c

void FUN_0800019c(undefined4 param_1)

{
  bool bVar1;
  
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setMainStackPointer(param_1);
  }
  return;
}


// ===== FUN_080001a4 @ 080001a4

void FUN_080001a4(void)

{
  (*DAT_080001c0)();
                    /* WARNING: Could not recover jumptable at 0x080001aa. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*DAT_080001c4)();
  return;
}


// ===== FUN_080001be @ 080001be

void FUN_080001be(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}


// ===== FUN_080001c8 @ 080001c8

longlong FUN_080001c8(uint param_1,int param_2,uint param_3,uint param_4)

{
  longlong lVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  bool bVar5;
  undefined8 uVar6;
  longlong lVar7;
  
  lVar1 = 0;
  iVar3 = 0x40;
  while (iVar4 = iVar3 + -1, 0 < iVar3) {
    uVar6 = FUN_080002ce(param_1,param_2,iVar4);
    uVar2 = (uint)((ulonglong)uVar6 >> 0x20);
    iVar3 = iVar4;
    if (param_4 < uVar2 || uVar2 - param_4 < (uint)(param_3 <= (uint)uVar6)) {
      uVar6 = FUN_080002b0(param_3,param_4,iVar4);
      bVar5 = param_1 < (uint)uVar6;
      param_1 = param_1 - (uint)uVar6;
      param_2 = (param_2 - (int)((ulonglong)uVar6 >> 0x20)) - (uint)bVar5;
      lVar7 = FUN_080002b0(1,0,iVar4);
      lVar1 = lVar7 + lVar1;
    }
  }
  return lVar1;
}


// ===== FUN_0800022c @ 0800022c

undefined4 FUN_0800022c(void)

{
  return DAT_08000230;
}


// ===== FUN_08000234 @ 08000234

int FUN_08000234(int param_1)

{
  if (param_1 - 0x41U < 0x1a) {
    param_1 = param_1 + 0x20;
  }
  return param_1;
}


// ===== FUN_08000240 @ 08000240

void FUN_08000240(undefined4 *param_1,undefined4 *param_2,uint param_3)

{
  undefined4 uVar1;
  bool bVar2;
  
  if ((((uint)param_1 | (uint)param_2) & 3) == 0) {
    for (; 3 < param_3; param_3 = param_3 - 4) {
      uVar1 = *param_2;
      param_2 = param_2 + 1;
      *param_1 = uVar1;
      param_1 = param_1 + 1;
    }
  }
  while (bVar2 = param_3 != 0, param_3 = param_3 - 1, bVar2) {
    *(undefined1 *)param_1 = *(undefined1 *)param_2;
    param_1 = (undefined4 *)((int)param_1 + 1);
    param_2 = (undefined4 *)((int)param_2 + 1);
  }
  return;
}


// ===== FUN_08000264 @ 08000264

void FUN_08000264(undefined1 *param_1,int param_2,undefined1 param_3)

{
  bool bVar1;
  
  while (bVar1 = param_2 != 0, param_2 = param_2 + -1, bVar1) {
    *param_1 = param_3;
    param_1 = param_1 + 1;
  }
  return;
}


// ===== FUN_08000272 @ 08000272

void FUN_08000272(undefined4 param_1,undefined4 param_2)

{
  FUN_08000264(param_1,param_2,0);
  return;
}


// ===== FUN_08000276 @ 08000276

undefined4 FUN_08000276(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  FUN_08000264(param_1,param_3,param_2);
  return param_1;
}


// ===== FUN_08000288 @ 08000288

int FUN_08000288(char *param_1)

{
  char cVar1;
  char *pcVar3;
  char *pcVar2;
  
  pcVar3 = param_1;
  do {
    pcVar2 = pcVar3 + 1;
    cVar1 = *pcVar3;
    pcVar3 = pcVar2;
  } while (cVar1 != '\0');
  return (int)pcVar2 - (int)(param_1 + 1);
}


// ===== FUN_08000296 @ 08000296

void FUN_08000296(int param_1,int param_2,uint param_3)

{
  uint uVar1;
  
  for (uVar1 = 0; (uVar1 < param_3 && (*(char *)(param_1 + uVar1) == *(char *)(param_2 + uVar1)));
      uVar1 = uVar1 + 1) {
  }
  return;
}


// ===== FUN_080002b0 @ 080002b0

longlong FUN_080002b0(uint param_1,int param_2,uint param_3)

{
  if ((int)param_3 < 0x20) {
    return CONCAT44(param_2 << (param_3 & 0xff) | param_1 >> (0x20 - param_3 & 0xff),
                    param_1 << (param_3 & 0xff));
  }
  return (ulonglong)(param_1 << (param_3 - 0x20 & 0xff)) << 0x20;
}


// ===== FUN_080002ce @ 080002ce

ulonglong FUN_080002ce(uint param_1,uint param_2,uint param_3)

{
  if ((int)param_3 < 0x20) {
    return CONCAT44(param_2 >> (param_3 & 0xff),
                    param_1 >> (param_3 & 0xff) | param_2 << (0x20 - param_3 & 0xff));
  }
  return (ulonglong)(param_2 >> (param_3 - 0x20 & 0xff));
}


// ===== FUN_080002f0 @ 080002f0

undefined4 FUN_080002f0(void)

{
  undefined4 *puVar1;
  byte *pbVar2;
  byte *pbVar3;
  byte *extraout_r1;
  byte *pbVar4;
  int extraout_r2;
  uint uVar5;
  int iVar6;
  uint uVar7;
  undefined4 *puVar8;
  uint uVar9;
  
  puVar1 = puRam08000310;
  for (puVar8 = puRam0800030c; puVar8 < puVar1; puVar8 = puVar8 + 4) {
    (*(code *)puVar8[3])(*puVar8,puVar8[1],puVar8[2]);
  }
  thunk_FUN_08005b4c();
  pbVar2 = (byte *)0x0;
  pbVar4 = extraout_r1;
  do {
    uVar9 = (uint)*pbVar2;
    uVar7 = uVar9 & 7;
    pbVar3 = pbVar2 + 1;
    if ((*pbVar2 & 7) == 0) {
      pbVar3 = pbVar2 + 2;
      uVar7 = (uint)pbVar2[1];
    }
    uVar5 = (int)uVar9 >> 4;
    if (uVar5 == 0) {
      uVar5 = (uint)*pbVar3;
      pbVar3 = pbVar3 + 1;
    }
    while (uVar7 = uVar7 - 1, uVar7 != 0) {
      *pbVar4 = *pbVar3;
      pbVar3 = pbVar3 + 1;
      pbVar4 = pbVar4 + 1;
    }
    if ((int)(uVar9 << 0x1c) < 0) {
      pbVar2 = pbVar3 + 1;
      iVar6 = uVar5 + 2;
      pbVar3 = pbVar4 + -(uint)*pbVar3;
      while (iVar6 = iVar6 + -1, -1 < iVar6) {
        *pbVar4 = *pbVar3;
        pbVar4 = pbVar4 + 1;
        pbVar3 = pbVar3 + 1;
      }
    }
    else {
      while (uVar5 = uVar5 - 1, pbVar2 = pbVar3, -1 < (int)uVar5) {
        *pbVar4 = 0;
        pbVar4 = pbVar4 + 1;
      }
    }
  } while (pbVar4 < extraout_r1 + extraout_r2);
  return 0;
}


// ===== FUN_08000314 @ 08000314

undefined4 FUN_08000314(byte *param_1,byte *param_2,int param_3)

{
  byte *pbVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  byte *pbVar5;
  uint uVar6;
  
  pbVar5 = param_2 + param_3;
  do {
    uVar6 = (uint)*param_1;
    uVar4 = uVar6 & 7;
    pbVar1 = param_1 + 1;
    if ((*param_1 & 7) == 0) {
      pbVar1 = param_1 + 2;
      uVar4 = (uint)param_1[1];
    }
    uVar2 = (int)uVar6 >> 4;
    if (uVar2 == 0) {
      uVar2 = (uint)*pbVar1;
      pbVar1 = pbVar1 + 1;
    }
    while (uVar4 = uVar4 - 1, uVar4 != 0) {
      *param_2 = *pbVar1;
      pbVar1 = pbVar1 + 1;
      param_2 = param_2 + 1;
    }
    if ((int)(uVar6 << 0x1c) < 0) {
      param_1 = pbVar1 + 1;
      iVar3 = uVar2 + 2;
      pbVar1 = param_2 + -(uint)*pbVar1;
      while (iVar3 = iVar3 + -1, -1 < iVar3) {
        *param_2 = *pbVar1;
        param_2 = param_2 + 1;
        pbVar1 = pbVar1 + 1;
      }
    }
    else {
      while (uVar2 = uVar2 - 1, param_1 = pbVar1, -1 < (int)uVar2) {
        *param_2 = 0;
        param_2 = param_2 + 1;
      }
    }
  } while (param_2 < pbVar5);
  return 0;
}


// ===== FUN_0800036a @ 0800036a

bool FUN_0800036a(void)

{
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 local_c;
  
  local_18 = 0;
  local_14 = 0;
  local_10 = 0;
  local_c = 0;
  local_1c = 0;
  FUN_080003d8(0x20,&local_18,0x10);
  FUN_08005912(&local_1c,&local_18,0xe);
  return local_c._2_2_ == (short)local_1c;
}


// ===== FUN_080003b0 @ 080003b0

undefined4 FUN_080003b0(void)

{
  undefined4 local_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  local_18 = *DAT_080003cc;
  uStack_14 = DAT_080003cc[1];
  uStack_10 = DAT_080003cc[2];
  uStack_c = DAT_080003cc[3];
  FUN_08000456(0x20,&local_18,0x10);
  return 0;
}


// ===== FUN_080003d0 @ 080003d0

void FUN_080003d0(void)

{
  FUN_08001fb8();
  return;
}


// ===== FUN_080003d8 @ 080003d8

void FUN_080003d8(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  FUN_080003ec(param_1,param_2,param_3);
  return;
}


// ===== FUN_080003ec @ 080003ec

void FUN_080003ec(uint param_1,undefined1 *param_2,short param_3)

{
  undefined1 uVar1;
  int iVar2;
  
  FUN_08002130();
  FUN_080020b4(((int)param_1 >> 8) * 2 + 0xa0U & 0xff);
  iVar2 = FUN_080021d0();
  if (iVar2 == 0) {
    FUN_080020b4(param_1 & 0xff);
    iVar2 = FUN_080021d0();
    if (iVar2 == 0) {
      FUN_08002130();
      FUN_080020b4(0xa1);
      iVar2 = FUN_080021d0();
      if (iVar2 == 0) {
        while (param_3 = param_3 + -1, param_3 != 0) {
          uVar1 = FUN_08002048(1);
          *param_2 = uVar1;
          param_2 = param_2 + 1;
        }
        uVar1 = FUN_08002048(0);
        *param_2 = uVar1;
        FUN_0800217c();
      }
    }
  }
  return;
}


// ===== FUN_08000456 @ 08000456

void FUN_08000456(uint param_1,int param_2,int param_3)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < (uint)((int)(param_3 + ((uint)(param_3 >> 0x1f) >> 0x1c)) >> 4);
      uVar1 = uVar1 + 1) {
    FUN_08000512(param_1,param_2,0x10);
    param_1 = param_1 + 0x10 & 0xffff;
    param_2 = param_2 + 0x10;
  }
  FUN_080004ee(param_1,param_2,
               param_3 + ((int)(param_3 + ((uint)(param_3 >> 0x1f) >> 0x1c)) >> 4) * -0x10 & 0xffff)
  ;
  return;
}


// ===== FUN_080004a4 @ 080004a4

void FUN_080004a4(uint param_1,undefined4 param_2)

{
  int iVar1;
  
  FUN_08002130();
  FUN_080020b4(((int)param_1 >> 8) * 2 + 0xa0U & 0xff);
  iVar1 = FUN_080021d0();
  if (iVar1 == 0) {
    FUN_080020b4(param_1 & 0xff);
    iVar1 = FUN_080021d0();
    if (iVar1 == 0) {
      FUN_080020b4(param_2);
      iVar1 = FUN_080021d0();
      if (iVar1 == 0) {
        FUN_0800217c();
        FUN_08000a30(5);
      }
    }
  }
  return;
}


// ===== FUN_080004ee @ 080004ee

void FUN_080004ee(uint param_1,undefined1 *param_2,uint param_3)

{
  bool bVar1;
  
  while (bVar1 = param_3 != 0, param_3 = param_3 - 1 & 0xffff, bVar1) {
    FUN_080004a4(param_1,*param_2);
    param_1 = param_1 + 1 & 0xffff;
    param_2 = param_2 + 1;
  }
  return;
}


// ===== FUN_08000512 @ 08000512

void FUN_08000512(uint param_1,undefined1 *param_2,uint param_3)

{
  int iVar1;
  bool bVar2;
  
  FUN_08002130();
  FUN_080020b4(((int)param_1 >> 8) * 2 + 0xa0U & 0xff);
  iVar1 = FUN_080021d0();
  if (iVar1 == 0) {
    FUN_080020b4(param_1 & 0xff);
    iVar1 = FUN_080021d0();
    if (iVar1 == 0) {
      while (bVar2 = param_3 != 0, param_3 = param_3 - 1 & 0xffff, bVar2) {
        FUN_080020b4(*param_2);
        iVar1 = FUN_080021d0();
        if (iVar1 != 0) {
          return;
        }
        param_2 = param_2 + 1;
      }
      FUN_0800217c();
    }
  }
  return;
}


// ===== FUN_08000566 @ 08000566

undefined4 FUN_08000566(void)

{
  int iVar1;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 local_c;
  
  local_c = 0;
  local_1c = 0;
  local_18 = 0;
  local_14 = 0;
  local_10 = 0;
  for (iVar1 = 0; iVar1 < 0x10; iVar1 = iVar1 + 1) {
    *(char *)((int)&local_1c + iVar1) = (char)iVar1 + 'a';
  }
  local_1c = CONCAT22(local_1c._2_2_,0xaa55);
  FUN_08005912(&local_c,&local_1c,0xe);
  local_10 = CONCAT13((char)((uint)local_c >> 8),CONCAT12((char)local_c,(undefined2)local_10));
  FUN_08000456(0x20,&local_1c,0x10);
  return 0;
}


// ===== thunk_FUN_080005c6 @ 080005c4

void thunk_FUN_080005c6(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}


// ===== FUN_080005c6 @ 080005c6

void FUN_080005c6(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}


// ===== FUN_08000668 @ 08000668

undefined4 FUN_08000668(undefined4 param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  if (*(int *)(*(int *)(DAT_0800069c + 700) + 0x214) == 0) {
    FUN_080036d8(DAT_0800069c,param_1,param_2);
    uVar1 = FUN_080037e6(DAT_0800069c);
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}


// ===== FUN_080006a0 @ 080006a0

void FUN_080006a0(void)

{
  return;
}


// ===== FUN_080006a2 @ 080006a2

void FUN_080006a2(void)

{
  return;
}


// ===== FUN_080006a4 @ 080006a4

void FUN_080006a4(int param_1,int param_2)

{
  uint *puVar1;
  uint *puVar2;
  uint uVar3;
  
  puVar1 = DAT_080006fc;
  uVar3 = 0;
  if (param_2 != 0) {
    if (param_2 == 1) {
      uVar3 = 0x100;
    }
    else if (param_2 == 2) {
      uVar3 = 0x200;
    }
    else {
      uVar3 = 0x300;
    }
  }
  *DAT_080006fc = *DAT_080006fc & 0xfffffcff;
  *puVar1 = *puVar1 | uVar3;
  *puVar1 = *puVar1 & 0xffffff07;
  puVar2 = DAT_080006fc;
  *DAT_080006fc = *puVar1 | param_1 << 3 | 2U;
  *puVar2 = *puVar2 | 0x10000;
  return;
}


// ===== FUN_08000700 @ 08000700

void FUN_08000700(void)

{
  uint *puVar1;
  
  puVar1 = DAT_08000774;
  if ((*DAT_08000774 & 0x200) != 0) {
    *DAT_08000774 = *DAT_08000774 & 0xfffffdff;
    *puVar1 = *puVar1 | 0x800;
    *puVar1 = *puVar1 & 0xfffff7ff;
    *puVar1 = *puVar1 | 0x200;
  }
  puVar1 = DAT_08000774;
  if ((*DAT_08000774 & 0x400) != 0) {
    *DAT_08000774 = *DAT_08000774 & 0xfffffbff;
    *puVar1 = *puVar1 | 0x1000;
    *puVar1 = *puVar1 & 0xffffefff;
    *puVar1 = *puVar1 | 0x400;
  }
  return;
}


// ===== FUN_08000778 @ 08000778

void FUN_08000778(int param_1)

{
  uint *puVar1;
  
  puVar1 = DAT_080007a4;
  *DAT_080007a4 = *DAT_080007a4 & 0xfffffcff;
  *puVar1 = *puVar1 | 4;
  *DAT_080007a4 = *puVar1 | param_1 << 8 | 0x10000U;
  return;
}


// ===== FUN_080007a8 @ 080007a8

void FUN_080007a8(undefined1 *param_1,undefined1 param_2)

{
  uint *puVar1;
  
  puVar1 = DAT_080007c8;
  *DAT_080007c8 = *DAT_080007c8 & 0xfffffcff;
  *puVar1 = *puVar1;
  *puVar1 = *puVar1 | 1;
  *param_1 = param_2;
  return;
}


// ===== FUN_080007cc @ 080007cc

void FUN_080007cc(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint *puVar1;
  
  puVar1 = DAT_08000804;
  *DAT_08000804 = *DAT_08000804 & 0xfffffcff;
  *puVar1 = *puVar1 | 0x300;
  *puVar1 = *puVar1 | 1;
  *param_1 = param_3;
  InstructionSynchronizationBarrier(0xf);
  param_1[1] = param_4;
  return;
}


// ===== FUN_08000808 @ 08000808

void FUN_08000808(undefined2 *param_1,undefined2 param_2)

{
  uint *puVar1;
  
  puVar1 = DAT_0800082c;
  *DAT_0800082c = *DAT_0800082c & 0xfffffcff;
  *puVar1 = *puVar1 | 0x100;
  *puVar1 = *puVar1 | 1;
  *param_1 = param_2;
  return;
}


// ===== FUN_08000830 @ 08000830

void FUN_08000830(undefined4 *param_1,undefined4 param_2)

{
  uint *puVar1;
  
  puVar1 = DAT_08000854;
  *DAT_08000854 = *DAT_08000854 & 0xfffffcff;
  *puVar1 = *puVar1 | 0x200;
  *puVar1 = *puVar1 | 1;
  *param_1 = param_2;
  return;
}


// ===== FUN_08000858 @ 08000858

void FUN_08000858(void)

{
  if ((*DAT_080008e8 & 0x10) != 0) {
    *(uint *)(DAT_080008ec + 0x1c) = *(uint *)(DAT_080008ec + 0x1c) | 0x10;
    *DAT_080008e8 = 0x10;
  }
  if ((*DAT_080008e8 & 0x20) != 0) {
    *(uint *)(DAT_080008ec + 0x1c) = *(uint *)(DAT_080008ec + 0x1c) | 8;
    *DAT_080008e8 = 0x20;
  }
  if ((*DAT_080008e8 & 0x40) != 0) {
    *(uint *)(DAT_080008ec + 0x1c) = *(uint *)(DAT_080008ec + 0x1c) | 4;
    *DAT_080008e8 = 0x40;
  }
  if ((*DAT_080008e8 & 0x80) != 0) {
    *(uint *)(DAT_080008ec + 0x1c) = *(uint *)(DAT_080008ec + 0x1c) | 2;
    *DAT_080008e8 = 0x80;
  }
  if ((*DAT_080008e8 & 2) != 0) {
    *(uint *)(DAT_080008ec + 0x1c) = *(uint *)(DAT_080008ec + 0x1c) | 0x20;
    *DAT_080008e8 = 2;
  }
  return;
}


// ===== FUN_080008f0 @ 080008f0

undefined4 FUN_080008f0(uint param_1)

{
  int iVar1;
  int iVar2;
  
  *(undefined4 *)(DAT_0800094c + 0x1c) = 0;
  iVar1 = FUN_08000f34();
  while ((*DAT_08000950 & 0x10000) != 0) {
    if ((param_1 != 0xffffffff) &&
       ((param_1 == 0 || (iVar2 = FUN_08000f34(), param_1 < (uint)(iVar2 - iVar1))))) {
      return 3;
    }
  }
  if ((*DAT_08000950 & 1) != 0) {
    *DAT_08000950 = 1;
  }
  if ((*DAT_08000950 & 0xf2) == 0) {
    return 0;
  }
  FUN_08000858();
  return 1;
}


// ===== FUN_08000954 @ 08000954

uint FUN_08000954(uint param_1)

{
  uint uVar1;
  
  uVar1 = 0;
  if ((param_1 < 0x8000000) || (DAT_080009dc <= param_1)) {
    if ((param_1 < DAT_080009dc) || (DAT_080009e0 <= param_1)) {
      if ((param_1 < DAT_080009e0) || (DAT_080009e4 <= param_1)) {
        if ((param_1 < DAT_080009e4) || (DAT_080009e8 <= param_1)) {
          if ((param_1 < DAT_080009e8) || (DAT_080009ec <= param_1)) {
            if ((param_1 < DAT_080009ec) || (DAT_080009f0 <= param_1)) {
              if ((param_1 < DAT_080009f0) || (DAT_080009f4 <= param_1)) {
                if ((param_1 < DAT_080009f4) || (DAT_080009f8 <= param_1)) {
                  uVar1 = 8;
                }
                else {
                  uVar1 = 7;
                }
              }
              else {
                uVar1 = 6;
              }
            }
            else {
              uVar1 = 5;
            }
          }
          else {
            uVar1 = 4;
          }
        }
        else {
          uVar1 = DAT_080009e4;
        }
      }
      else {
        uVar1 = 2;
      }
    }
    else {
      uVar1 = 1;
    }
  }
  return uVar1;
}


// ===== FUN_080009fc @ 080009fc

void FUN_080009fc(void)

{
  int iVar1;
  
  iVar1 = DAT_08000a28[1];
  if (*DAT_08000a28 + DAT_08000a28[2] != 0) {
    FUN_08002238(*DAT_08000a28 + DAT_08000a28[2],DAT_08000a2c,8);
    FUN_08002238(iVar1,DAT_08000a2c + 0x10,4);
  }
  return;
}


// ===== FUN_08000a30 @ 08000a30

void FUN_08000a30(uint param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_08000f34();
  if (param_1 != 0xffffffff) {
    param_1 = param_1 + *DAT_08000a54;
  }
  do {
    iVar2 = FUN_08000f34();
  } while ((uint)(iVar2 - iVar1) < param_1);
  return;
}


// ===== FUN_08000a58 @ 08000a58

int FUN_08000a58(int *param_1,uint *param_2)

{
  int iVar1;
  uint uVar2;
  
  if (*(char *)(DAT_08000afc + 0x18) == '\x01') {
    iVar1 = 2;
  }
  else {
    *(undefined1 *)(DAT_08000afc + 0x18) = 1;
    iVar1 = FUN_080008f0(50000);
    if (iVar1 == 0) {
      *param_2 = 0xffffffff;
      if (*param_1 == 1) {
        FUN_08000778((char)param_1[4],param_1[1]);
        iVar1 = FUN_080008f0(50000);
        *DAT_08000b00 = *DAT_08000b00 & 0xfffffffb;
      }
      else {
        uVar2 = param_1[2];
        while( true ) {
          if ((uint)(param_1[3] + param_1[2]) <= uVar2) break;
          FUN_080006a4(uVar2,(char)param_1[4]);
          iVar1 = FUN_080008f0(50000);
          *DAT_08000b00 = *DAT_08000b00 & 0xffffff05;
          if (iVar1 != 0) {
            *param_2 = uVar2;
            break;
          }
          uVar2 = uVar2 + 1;
        }
      }
      FUN_08000700();
    }
    *(undefined1 *)(DAT_08000afc + 0x18) = 0;
  }
  return iVar1;
}


// ===== FUN_08000b04 @ 08000b04

int FUN_08000b04(int param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  undefined8 uVar2;
  
  if (*(char *)(DAT_08000b94 + 0x18) == '\x01') {
    iVar1 = 2;
  }
  else {
    *(undefined1 *)(DAT_08000b94 + 0x18) = 1;
    uVar2 = FUN_080008f0(50000);
    iVar1 = (int)uVar2;
    if (iVar1 == 0) {
      if (param_1 == 0) {
        FUN_080007a8(param_2,param_3 & 0xff);
      }
      else if (param_1 == 1) {
        FUN_08000808(param_2,param_3 & 0xffff);
      }
      else if (param_1 == 2) {
        FUN_08000830(param_2,param_3);
      }
      else {
        FUN_080007cc(param_2,(int)((ulonglong)uVar2 >> 0x20),param_3,param_4);
      }
      iVar1 = FUN_080008f0(50000);
      *DAT_08000b98 = *DAT_08000b98 & 0xfffffffe;
    }
    *(undefined1 *)(DAT_08000b94 + 0x18) = 0;
  }
  return iVar1;
}


// ===== FUN_08000b9c @ 08000b9c

undefined4 FUN_08000b9c(void)

{
  undefined4 uVar1;
  uint *puVar2;
  
  uVar1 = 0;
  if ((*DAT_08000bc4 & 0x80000000) != 0) {
    puVar2 = DAT_08000bc4 + -3;
    *puVar2 = DAT_08000bc8;
    *puVar2 = DAT_08000bcc;
    if ((*DAT_08000bc4 & 0x80000000) != 0) {
      uVar1 = 1;
    }
  }
  return uVar1;
}


// ===== FUN_08000bd0 @ 08000bd0

void FUN_08000bd0(uint *param_1,uint param_2)

{
  uint *puVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  
  for (uVar2 = 0; puVar1 = DAT_08000d30, uVar2 < 0x10; uVar2 = uVar2 + 1) {
    uVar4 = 1 << (uVar2 & 0xff);
    uVar3 = param_2 & uVar4;
    if (uVar3 == uVar4) {
      if (param_1 == DAT_08000d10) {
        iVar5 = 0;
      }
      else if (param_1 == DAT_08000d14) {
        iVar5 = 1;
      }
      else if (param_1 == DAT_08000d18) {
        iVar5 = 2;
      }
      else if (param_1 == DAT_08000d1c) {
        iVar5 = 3;
      }
      else if (param_1 == DAT_08000d20) {
        iVar5 = 4;
      }
      else if (param_1 == DAT_08000d24) {
        iVar5 = 5;
      }
      else if (param_1 == DAT_08000d28) {
        iVar5 = 6;
      }
      else if (param_1 == DAT_08000d2c) {
        iVar5 = 7;
      }
      else {
        iVar5 = 8;
      }
      if (iVar5 << ((uVar2 & 3) << 2) ==
          (*(uint *)(DAT_08000d0c + (uVar2 & 0xfffffffc)) & 0xf << ((uVar2 & 3) << 2))) {
        *DAT_08000d30 = *DAT_08000d30 & ~uVar3;
        puVar1[1] = puVar1[1] & ~uVar3;
        puVar1[2] = puVar1[2] & ~uVar3;
        puVar1[3] = puVar1[3] & ~uVar3;
        *(uint *)(DAT_08000d0c + (uVar2 & 0xfffffffc)) =
             *(uint *)(DAT_08000d0c + (uVar2 & 0xfffffffc)) & ~(0xf << ((uVar2 & 3) << 2));
      }
      *param_1 = *param_1 & ~(3 << ((uVar2 & 0x7f) << 1));
      param_1[(uVar2 >> 3) + 8] = param_1[(uVar2 >> 3) + 8] & ~(0xf << ((uVar2 & 7) << 2));
      param_1[3] = param_1[3] & ~(3 << ((uVar2 & 0x7f) << 1));
      param_1[1] = param_1[1] & ~(1 << (uVar2 & 0xff));
      param_1[2] = param_1[2] & ~(3 << ((uVar2 & 0x7f) << 1));
    }
  }
  return;
}


// ===== FUN_08000d34 @ 08000d34

uint FUN_08000d34(uint *param_1,uint *param_2)

{
  uint *puVar1;
  uint *puVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  
  uVar3 = 0;
  for (uVar4 = 0; uVar4 < 0x10; uVar4 = uVar4 + 1) {
    uVar6 = 1 << (uVar4 & 0xff);
    uVar5 = *param_2 & uVar6;
    if (uVar5 == uVar6) {
      if ((((param_2[1] == 1) || (param_2[1] == 2)) || (param_2[1] == 0x11)) || (param_2[1] == 0x12)
         ) {
        param_1[2] = param_1[2] & ~(3 << ((uVar4 & 0x7f) << 1)) |
                     param_2[3] << ((uVar4 & 0x7f) << 1);
        param_1[1] = param_1[1] & ~(1 << (uVar4 & 0xff)) |
                     (((byte)param_2[1] & 0x1f) >> 4) << (uVar4 & 0xff);
      }
      param_1[3] = param_1[3] & ~(3 << ((uVar4 & 0x7f) << 1)) | param_2[2] << ((uVar4 & 0x7f) << 1);
      if ((param_2[1] == 2) || (param_2[1] == 0x12)) {
        param_1[(uVar4 >> 3) + 8] =
             param_1[(uVar4 >> 3) + 8] & ~(0xf << ((uVar4 & 7) << 2)) |
             param_2[4] << ((uVar4 & 7) << 2);
      }
      uVar3 = *param_1 & ~(3 << ((uVar4 & 0x7f) << 1)) |
              ((byte)param_2[1] & 3) << ((uVar4 & 0x7f) << 1);
      *param_1 = uVar3;
      if ((param_2[1] & 0x10000000) == 0x10000000) {
        *DAT_08000f08 = *DAT_08000f08 | 0x4000;
        if (param_1 == DAT_08000f10) {
          iVar7 = 0;
        }
        else if (param_1 == DAT_08000f14) {
          iVar7 = 1;
        }
        else if (param_1 == DAT_08000f18) {
          iVar7 = 2;
        }
        else if (param_1 == DAT_08000f1c) {
          iVar7 = 3;
        }
        else if (param_1 == DAT_08000f20) {
          iVar7 = 4;
        }
        else if (param_1 == DAT_08000f24) {
          iVar7 = 5;
        }
        else if (param_1 == DAT_08000f28) {
          iVar7 = 6;
        }
        else if (param_1 == DAT_08000f2c) {
          iVar7 = 7;
        }
        else {
          iVar7 = 8;
        }
        *(uint *)(DAT_08000f0c + (uVar4 & 0xfffffffc)) =
             *(uint *)(DAT_08000f0c + (uVar4 & 0xfffffffc)) & ~(0xf << ((uVar4 & 3) << 2)) |
             iVar7 << ((uVar4 & 3) << 2);
        puVar1 = DAT_08000f30;
        uVar3 = *DAT_08000f30 & ~uVar5;
        if ((param_2[1] & 0x10000) == 0x10000) {
          uVar3 = uVar3 | uVar5;
        }
        *DAT_08000f30 = uVar3;
        puVar2 = DAT_08000f30;
        uVar3 = puVar1[1] & ~uVar5;
        if ((param_2[1] & 0x20000) == 0x20000) {
          uVar3 = uVar3 | uVar5;
        }
        DAT_08000f30[1] = uVar3;
        puVar1 = DAT_08000f30;
        uVar3 = puVar2[2] & ~uVar5;
        if ((param_2[1] & 0x100000) == 0x100000) {
          uVar3 = uVar3 | uVar5;
        }
        DAT_08000f30[2] = uVar3;
        uVar3 = puVar1[3] & ~uVar5;
        if ((param_2[1] & 0x200000) == 0x200000) {
          uVar3 = uVar3 | uVar5;
        }
        DAT_08000f30[3] = uVar3;
      }
    }
  }
  return uVar3;
}


// ===== FUN_08000f34 @ 08000f34

undefined4 FUN_08000f34(void)

{
  return *DAT_08000f3c;
}


// ===== FUN_08000f40 @ 08000f40

void FUN_08000f40(void)

{
  *DAT_08000f50 = *DAT_08000f50 + (uint)*DAT_08000f54;
  return;
}


// ===== FUN_08000f58 @ 08000f58

undefined4 FUN_08000f58(void)

{
  uint *puVar1;
  
  puVar1 = DAT_08000f90;
  *DAT_08000f90 = *DAT_08000f90 | 0x200;
  *puVar1 = *puVar1 | 0x400;
  *puVar1 = *puVar1 | 0x100;
  FUN_08001108(3);
  FUN_08000f94(0);
  FUN_08000fe0();
  return 0;
}


// ===== FUN_08000f94 @ 08000f94

undefined4 FUN_08000f94(uint param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_08001e3c((int)((ulonglong)*DAT_08000fd8 / (1000 / (ulonglong)*DAT_08000fd4)));
  if (iVar1 == 0) {
    if (param_1 < 0x10) {
      FUN_0800108c(0xffffffff,param_1);
      *DAT_08000fdc = param_1;
      uVar2 = 0;
    }
    else {
      uVar2 = 1;
    }
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}


// ===== FUN_08000fe0 @ 08000fe0

void FUN_08000fe0(void)

{
  uint *puVar1;
  
  puVar1 = DAT_08001024;
  *DAT_08001024 = *DAT_08001024 | 0x4000;
  puVar1[-1] = puVar1[-1] | 0x10000000;
  return;
}


// ===== FUN_08001028 @ 08001028

void FUN_08001028(uint param_1)

{
  if (-1 < (int)param_1) {
    *(int *)(DAT_08001068 + (param_1 >> 5) * 4) = 1 << (param_1 & 0x1f);
    DataSynchronizationBarrier(0xf);
    InstructionSynchronizationBarrier(0xf);
  }
  return;
}


// ===== FUN_0800106c @ 0800106c

void FUN_0800106c(uint param_1)

{
  if (-1 < (int)param_1) {
    *(int *)((param_1 >> 5) * 4 + -0x1fff1f00) = 1 << (param_1 & 0x1f);
  }
  return;
}


// ===== FUN_0800108c @ 0800108c

void FUN_0800108c(undefined4 param_1,uint param_2,uint param_3)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = FUN_08005894();
  uVar1 = uVar1 & 7;
  if (7 - uVar1 < 5) {
    uVar2 = 7 - uVar1;
  }
  else {
    uVar2 = 4;
  }
  if (uVar1 + 4 < 7) {
    uVar1 = 0;
  }
  else {
    uVar1 = uVar1 - 3;
  }
  FUN_080058cc(param_1,((1 << (uVar2 & 0xff)) - 1U & param_2) << (uVar1 & 0xff) |
                       (1 << (uVar1 & 0xff)) - 1U & param_3);
  return;
}


// ===== FUN_08001108 @ 08001108

void FUN_08001108(uint param_1)

{
  *DAT_08001128 = DAT_0800112c | *DAT_08001128 & 0xf8ff | (param_1 & 7) << 8;
  return;
}


// ===== FUN_08001130 @ 08001130

void FUN_08001130(void)

{
  return;
}


// ===== FUN_08001132 @ 08001132

undefined4 FUN_08001132(int *param_1,undefined4 param_2)

{
  *(undefined4 *)(*param_1 + 0x24) = param_2;
  return 0;
}


// ===== FUN_0800113c @ 0800113c

undefined4 FUN_0800113c(int *param_1,int param_2,int param_3)

{
  uint uVar1;
  uint uVar2;
  
  if (param_2 == 0) {
    *(uint *)(*param_1 + 0x28) = *(uint *)(*param_1 + 0x24) | param_3 << 0x10;
  }
  else {
    uVar2 = *(uint *)(*param_1 + 0x24) + (*(uint *)(*param_1 + 0x28) >> 0x10);
    for (uVar1 = 0; uVar1 < param_2 - 1U; uVar1 = uVar1 + 1 & 0xff) {
      uVar2 = uVar2 + (*(uint *)(*param_1 + 0x104 + uVar1 * 4) >> 0x10);
    }
    *(uint *)(*param_1 + 0x104 + (param_2 + -1) * 4) = uVar2 | param_3 << 0x10;
  }
  return 0;
}


// ===== FUN_0800118a @ 0800118a

void FUN_0800118a(int param_1)

{
  FUN_08003ffc(*(undefined4 *)(param_1 + 0x404));
  return;
}


// ===== FUN_08001198 @ 08001198

void FUN_08001198(int param_1,int param_2)

{
  FUN_08003e66(*(undefined4 *)(param_1 + 0x404),param_2,
               *(undefined4 *)(param_1 + param_2 * 0x1c + 0x48));
  return;
}


// ===== FUN_080011b8 @ 080011b8

void FUN_080011b8(int param_1,int param_2)

{
  FUN_08003f4c(*(undefined4 *)(param_1 + 0x404),param_2,
               *(undefined4 *)(param_1 + param_2 * 0x1c + 0x208));
  return;
}


// ===== FUN_080011d8 @ 080011d8

bool FUN_080011d8(int param_1)

{
  if (param_1 != 0) {
    *(undefined1 *)(param_1 + 0x3bd) = 3;
    FUN_08001d72(param_1);
    FUN_08001bb8(param_1);
    *(undefined1 *)(param_1 + 0x3bd) = 0;
  }
  return param_1 == 0;
}


// ===== FUN_080011fe @ 080011fe

void FUN_080011fe(int param_1)

{
  FUN_08004002(*(undefined4 *)(param_1 + 0x404));
  return;
}


// ===== FUN_0800120c @ 0800120c

undefined4 FUN_0800120c(undefined4 *param_1,uint param_2)

{
  undefined4 uVar1;
  byte *pbVar2;
  
  if ((param_2 & 0x80) == 0x80) {
    pbVar2 = (byte *)(param_1 + (param_2 & 0xf) * 7 + 0xf);
    pbVar2[1] = 1;
  }
  else {
    pbVar2 = (byte *)(param_1 + (param_2 & 0xf) * 7 + 0x7f);
    pbVar2[1] = 0;
  }
  *pbVar2 = (byte)param_2 & 0xf;
  if (*(char *)(param_1 + 0xef) == '\x01') {
    uVar1 = 2;
  }
  else {
    *(undefined1 *)(param_1 + 0xef) = 1;
    FUN_08004a30(*param_1,pbVar2);
    uVar1 = 0;
    *(undefined1 *)(param_1 + 0xef) = 0;
  }
  return uVar1;
}


// ===== FUN_08001276 @ 08001276

undefined4 FUN_08001276(undefined4 *param_1,uint param_2)

{
  undefined4 uVar1;
  byte *pbVar2;
  
  if ((uint)param_1[1] < (param_2 & 0xf)) {
    uVar1 = 1;
  }
  else {
    if ((param_2 & 0x80) == 0x80) {
      pbVar2 = (byte *)(param_1 + (param_2 & 0xf) * 7 + 0xf);
      pbVar2[1] = 1;
    }
    else {
      pbVar2 = (byte *)(param_1 + (param_2 & 0xf) * 7 + 0x7f);
      pbVar2[1] = 0;
    }
    pbVar2[2] = 0;
    *pbVar2 = (byte)param_2 & 0xf;
    if (*(char *)(param_1 + 0xef) == '\x01') {
      uVar1 = 2;
    }
    else {
      *(undefined1 *)(param_1 + 0xef) = 1;
      FUN_08004ff4(*param_1,pbVar2);
      uVar1 = 0;
      *(undefined1 *)(param_1 + 0xef) = 0;
    }
  }
  return uVar1;
}


// ===== FUN_080012f2 @ 080012f2

undefined4 FUN_080012f2(int param_1,uint param_2)

{
  return *(undefined4 *)(param_1 + (param_2 & 0xf) * 0x1c + 0x214);
}


// ===== FUN_08001308 @ 08001308

undefined4 FUN_08001308(undefined4 *param_1,uint param_2,undefined4 param_3,int param_4)

{
  undefined4 uVar1;
  byte *pbVar2;
  
  if ((param_2 & 0x80) == 0x80) {
    pbVar2 = (byte *)(param_1 + (param_2 & 0xf) * 7 + 0xf);
    pbVar2[1] = 1;
  }
  else {
    pbVar2 = (byte *)(param_1 + (param_2 & 0xf) * 7 + 0x7f);
    pbVar2[1] = 0;
  }
  *pbVar2 = (byte)param_2 & 0xf;
  *(undefined4 *)(pbVar2 + 8) = param_3;
  pbVar2[3] = (byte)param_4;
  if (pbVar2[1] != 0) {
    *(ushort *)(pbVar2 + 6) = (ushort)*pbVar2;
  }
  if (param_4 == 2) {
    pbVar2[4] = 0;
  }
  if (*(char *)(param_1 + 0xef) == '\x01') {
    uVar1 = 2;
  }
  else {
    *(undefined1 *)(param_1 + 0xef) = 1;
    FUN_08004868(*param_1,pbVar2);
    *(undefined1 *)(param_1 + 0xef) = 0;
    uVar1 = 0;
  }
  return uVar1;
}


// ===== FUN_08001394 @ 08001394

undefined4 FUN_08001394(undefined4 *param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  byte *pbVar1;
  
  pbVar1 = (byte *)(param_1 + (param_2 & 0xf) * 7 + 0x7f);
  *(undefined4 *)(pbVar1 + 0xc) = param_3;
  *(undefined4 *)(pbVar1 + 0x14) = param_4;
  pbVar1[0x18] = 0;
  pbVar1[0x19] = 0;
  pbVar1[0x1a] = 0;
  pbVar1[0x1b] = 0;
  pbVar1[1] = 0;
  *pbVar1 = (byte)param_2 & 0xf;
  if (param_1[4] == 1) {
    *(undefined4 *)(pbVar1 + 0x10) = param_3;
  }
  if ((param_2 & 0xf) == 0) {
    FUN_08004dac(*param_1,pbVar1,*(undefined1 *)(param_1 + 4));
  }
  else {
    FUN_0800511c(*param_1,pbVar1,*(undefined1 *)(param_1 + 4));
  }
  return 0;
}


// ===== FUN_080013ec @ 080013ec

undefined4 FUN_080013ec(undefined4 *param_1,uint param_2)

{
  undefined4 uVar1;
  byte *pbVar2;
  
  if ((uint)param_1[1] < (param_2 & 0xf)) {
    uVar1 = 1;
  }
  else {
    if ((param_2 & 0x80) == 0x80) {
      pbVar2 = (byte *)(param_1 + (param_2 & 0xf) * 7 + 0xf);
      pbVar2[1] = 1;
    }
    else {
      pbVar2 = (byte *)(param_1 + param_2 * 7 + 0x7f);
      pbVar2[1] = 0;
    }
    pbVar2[2] = 1;
    *pbVar2 = (byte)param_2 & 0xf;
    if (*(char *)(param_1 + 0xef) == '\x01') {
      uVar1 = 2;
    }
    else {
      *(undefined1 *)(param_1 + 0xef) = 1;
      FUN_08005082(*param_1,pbVar2);
      if ((param_2 & 0xf) == 0) {
        FUN_08004f84(*param_1,*(undefined1 *)(param_1 + 4),param_1 + 0xf1);
      }
      uVar1 = 0;
      *(undefined1 *)(param_1 + 0xef) = 0;
    }
  }
  return uVar1;
}


// ===== FUN_08001476 @ 08001476

undefined4 FUN_08001476(undefined4 *param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  byte *pbVar1;
  
  pbVar1 = (byte *)(param_1 + (param_2 & 0xf) * 7 + 0xf);
  *(undefined4 *)(pbVar1 + 0xc) = param_3;
  *(undefined4 *)(pbVar1 + 0x14) = param_4;
  pbVar1[0x18] = 0;
  pbVar1[0x19] = 0;
  pbVar1[0x1a] = 0;
  pbVar1[0x1b] = 0;
  pbVar1[1] = 1;
  *pbVar1 = (byte)param_2 & 0xf;
  if (param_1[4] == 1) {
    *(undefined4 *)(pbVar1 + 0x10) = param_3;
  }
  if ((param_2 & 0xf) == 0) {
    FUN_08004dac(*param_1,pbVar1,*(undefined1 *)(param_1 + 4));
  }
  else {
    FUN_0800511c(*param_1,pbVar1,*(undefined1 *)(param_1 + 4));
  }
  return 0;
}


// ===== FUN_080014d0 @ 080014d0

void FUN_080014d0(int *param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  undefined4 uVar5;
  uint uVar6;
  
  iVar1 = *param_1;
  iVar2 = FUN_080054f2(*param_1);
  if ((iVar2 == 0) && (iVar2 = FUN_08005644(*param_1), iVar2 != 0)) {
    uVar3 = FUN_08005644(*param_1);
    if ((uVar3 & 2) == 2) {
      *(uint *)(*param_1 + 0x14) = *(uint *)(*param_1 + 0x14) & 2;
    }
    uVar3 = FUN_08005644(*param_1);
    if ((uVar3 & 0x10) == 0x10) {
      *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) & 0xffffffef;
      uVar6 = *(uint *)(iVar1 + 0x20);
      uVar3 = uVar6 & 0xf;
      if ((uVar6 & 0x1fffff) >> 0x11 == 2) {
        if ((uVar6 & 0x7ff0) != 0) {
          FUN_0800564e(iVar1,param_1[uVar3 * 7 + 0x82],(uVar6 & 0x7fff) >> 4);
          param_1[uVar3 * 7 + 0x82] = param_1[uVar3 * 7 + 0x82] + ((uVar6 & 0x7fff) >> 4);
          param_1[uVar3 * 7 + 0x85] = param_1[uVar3 * 7 + 0x85] + ((uVar6 & 0x7fff) >> 4);
        }
      }
      else if ((uVar6 & 0x1fffff) >> 0x11 == 6) {
        FUN_0800564e(iVar1,param_1 + 0xf1,8);
        param_1[uVar3 * 7 + 0x85] = param_1[uVar3 * 7 + 0x85] + ((uVar6 & 0x7fff) >> 4);
      }
      *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) | 0x10;
    }
    uVar3 = FUN_08005644(*param_1);
    if ((uVar3 & 0x80000) == 0x80000) {
      uVar6 = 0;
      for (uVar3 = FUN_080055e4(*param_1); uVar3 != 0; uVar3 = uVar3 >> 1) {
        if ((uVar3 & 1) != 0) {
          uVar4 = FUN_0800562a(*param_1,uVar6 & 0xff);
          if ((uVar4 & 1) != 0) {
            *(undefined4 *)(iVar1 + uVar6 * 0x20 + 0xb08) = 1;
            FUN_08002a88(param_1,uVar6);
          }
          if ((uVar4 & 8) == 8) {
            *(undefined4 *)(iVar1 + uVar6 * 0x20 + 0xb08) = 8;
            FUN_08002a24(param_1,uVar6);
          }
          if ((uVar4 & 0x10) == 0x10) {
            *(undefined4 *)(iVar1 + uVar6 * 0x20 + 0xb08) = 0x10;
          }
          if ((uVar4 & 0x20) == 0x20) {
            *(undefined4 *)(iVar1 + uVar6 * 0x20 + 0xb08) = 0x20;
          }
          if ((uVar4 & 0x2000) == 0x2000) {
            *(undefined4 *)(iVar1 + uVar6 * 0x20 + 0xb08) = 0x2000;
          }
        }
        uVar6 = uVar6 + 1;
      }
    }
    uVar3 = FUN_08005644(*param_1);
    if ((uVar3 & 0x40000) == 0x40000) {
      uVar3 = FUN_080055d0(*param_1);
      uVar6 = 0;
      for (; uVar3 != 0; uVar3 = uVar3 >> 1) {
        if ((uVar3 & 1) != 0) {
          uVar4 = FUN_080055f8(*param_1,uVar6 & 0xff);
          if ((uVar4 & 1) != 0) {
            *(uint *)(iVar1 + 0x834) = *(uint *)(iVar1 + 0x834) & ~(1 << (uVar6 & 0xf));
            *(undefined4 *)(iVar1 + uVar6 * 0x20 + 0x908) = 1;
            if (((param_1[4] == 1) &&
                (param_1[uVar6 * 7 + 0x12] = param_1[uVar6 * 7 + 0x12] + param_1[uVar6 * 7 + 0x11],
                uVar6 == 0)) && (param_1[0x14] == 0)) {
              FUN_08004f84(*param_1,1,param_1 + 0xf1);
            }
            FUN_08001198(param_1,uVar6 & 0xff);
          }
          if ((uVar4 & 8) == 8) {
            *(undefined4 *)(iVar1 + uVar6 * 0x20 + 0x908) = 8;
          }
          if ((uVar4 & 0x10) == 0x10) {
            *(undefined4 *)(iVar1 + uVar6 * 0x20 + 0x908) = 0x10;
          }
          if ((uVar4 & 0x40) == 0x40) {
            *(undefined4 *)(iVar1 + uVar6 * 0x20 + 0x908) = 0x40;
          }
          if ((uVar4 & 2) == 2) {
            *(undefined4 *)(iVar1 + uVar6 * 0x20 + 0x908) = 2;
          }
          if ((uVar4 & 0x80) == 0x80) {
            FUN_08002c04(param_1,uVar6);
          }
        }
        uVar6 = uVar6 + 1;
      }
    }
    uVar3 = FUN_08005644(*param_1);
    if ((uVar3 & 0x80000000) == 0x80000000) {
      *(uint *)(iVar1 + 0x804) = *(uint *)(iVar1 + 0x804) & 0xfffffffe;
      if ((char)param_1[0xfd] == '\x01') {
        *(undefined1 *)(param_1 + 0xfd) = 0;
        FUN_08001130(param_1,0);
      }
      else {
        FUN_08001cc4(param_1);
      }
      *(uint *)(*param_1 + 0x14) = *(uint *)(*param_1 + 0x14) & 0x80000000;
    }
    uVar3 = FUN_08005644(*param_1);
    if ((uVar3 & 0x800) == 0x800) {
      if ((*(uint *)(iVar1 + 0x808) & 1) != 0) {
        FUN_08001dbc(param_1);
      }
      *(uint *)(*param_1 + 0x14) = *(uint *)(*param_1 + 0x14) & 0x800;
    }
    uVar3 = FUN_08005644(*param_1);
    if ((uVar3 & 0x1000) == 0x1000) {
      *(uint *)(iVar1 + 0x804) = *(uint *)(iVar1 + 0x804) & 0xfffffffe;
      FUN_0800549c(*param_1,0x10);
      for (uVar3 = 0; uVar3 < (uint)param_1[1]; uVar3 = uVar3 + 1) {
        *(undefined4 *)(iVar1 + uVar3 * 0x20 + 0x908) = 0xfb7f;
        *(uint *)(iVar1 + 0x900 + uVar3 * 0x20) =
             *(uint *)(iVar1 + 0x900 + uVar3 * 0x20) & 0xffdfffff;
        *(uint *)(iVar1 + 0x900 + uVar3 * 0x20) =
             *(uint *)(iVar1 + 0x900 + uVar3 * 0x20) | 0x8000000;
        *(undefined4 *)(iVar1 + uVar3 * 0x20 + 0xb08) = 0xfb7f;
        *(uint *)(iVar1 + 0xb00 + uVar3 * 0x20) =
             *(uint *)(iVar1 + 0xb00 + uVar3 * 0x20) & 0xffdfffff;
        *(uint *)(iVar1 + 0xb00 + uVar3 * 0x20) =
             *(uint *)(iVar1 + 0xb00 + uVar3 * 0x20) | 0x8000000;
      }
      *(uint *)(iVar1 + 0x81c) = *(uint *)(iVar1 + 0x81c) | 0x10001;
      if (param_1[0xc] == 0) {
        *(uint *)(iVar1 + 0x814) = *(uint *)(iVar1 + 0x814) | 0x202b;
        *(uint *)(iVar1 + 0x810) = *(uint *)(iVar1 + 0x810) | 0xb;
      }
      else {
        *(uint *)(iVar1 + 0x884) = *(uint *)(iVar1 + 0x884) | 0xb;
        *(uint *)(iVar1 + 0x844) = *(uint *)(iVar1 + 0x844) | 0xb;
      }
      *(uint *)(iVar1 + 0x800) = *(uint *)(iVar1 + 0x800) & 0xfffff80f;
      FUN_08004f84(*param_1,(char)param_1[4],param_1 + 0xf1);
      *(uint *)(*param_1 + 0x14) = *(uint *)(*param_1 + 0x14) & 0x1000;
    }
    uVar3 = FUN_08005644(*param_1);
    if ((uVar3 & 0x2000) == 0x2000) {
      FUN_08004938(*param_1);
      iVar1 = FUN_080054cc(*param_1);
      param_1[3] = iVar1;
      uVar5 = FUN_08001df0();
      FUN_080056e4(*param_1,uVar5,(char)param_1[3]);
      FUN_08001c94(param_1);
      *(uint *)(*param_1 + 0x14) = *(uint *)(*param_1 + 0x14) & 0x2000;
    }
    uVar3 = FUN_08005644(*param_1);
    if ((uVar3 & 8) == 8) {
      FUN_08001cd2(param_1);
      *(uint *)(*param_1 + 0x14) = *(uint *)(*param_1 + 0x14) & 8;
    }
    uVar3 = FUN_08005644(*param_1);
    if ((uVar3 & 0x100000) == 0x100000) {
      FUN_08001a2c(param_1,0);
      *(uint *)(*param_1 + 0x14) = *(uint *)(*param_1 + 0x14) & 0x100000;
    }
    uVar3 = FUN_08005644(*param_1);
    if ((uVar3 & 0x200000) == 0x200000) {
      FUN_08001a3e(param_1,0);
      *(uint *)(*param_1 + 0x14) = *(uint *)(*param_1 + 0x14) & 0x200000;
    }
    uVar3 = FUN_08005644(*param_1);
    if ((uVar3 & 0x40000000) == 0x40000000) {
      FUN_0800118a(param_1);
      *(uint *)(*param_1 + 0x14) = *(uint *)(*param_1 + 0x14) & 0x40000000;
    }
    uVar3 = FUN_08005644(*param_1);
    if ((uVar3 & 4) == 4) {
      uVar3 = *(uint *)(*param_1 + 4);
      if ((uVar3 & 4) == 4) {
        FUN_080011fe(param_1);
      }
      *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) | uVar3;
    }
  }
  return;
}


// ===== FUN_08001a2c @ 08001a2c

void FUN_08001a2c(int param_1,undefined4 param_2)

{
  FUN_080040d4(*(undefined4 *)(param_1 + 0x404),param_2);
  return;
}


// ===== FUN_08001a3e @ 08001a3e

void FUN_08001a3e(int param_1,undefined4 param_2)

{
  FUN_080040da(*(undefined4 *)(param_1 + 0x404),param_2);
  return;
}


// ===== FUN_08001a50 @ 08001a50

undefined4 FUN_08001a50(int *param_1)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  undefined1 auStack_38 [40];
  
  if (param_1 == (int *)0x0) {
    uVar1 = 1;
  }
  else {
    iVar3 = *param_1;
    if (*(char *)((int)param_1 + 0x3bd) == '\0') {
      *(undefined1 *)(param_1 + 0xef) = 0;
      FUN_08001bec(param_1);
    }
    *(undefined1 *)((int)param_1 + 0x3bd) = 3;
    if ((*(uint *)(iVar3 + 0x3c) & 0x100) == 0) {
      param_1[4] = 0;
    }
    FUN_08004d9c(*param_1);
    FUN_08000240(auStack_38,param_1 + 4,0x28);
    iVar3 = FUN_08004960(*param_1,param_1[1],param_1[2],param_1[3]);
    if (iVar3 == 0) {
      FUN_08005670(*param_1,0);
      for (uVar2 = 0; uVar2 < (uint)param_1[1]; uVar2 = uVar2 + 1 & 0xff) {
        *(undefined1 *)((int)param_1 + uVar2 * 0x1c + 0x3d) = 1;
        *(char *)(param_1 + uVar2 * 7 + 0xf) = (char)uVar2;
        *(short *)((int)param_1 + uVar2 * 0x1c + 0x42) = (short)uVar2;
        *(undefined1 *)((int)param_1 + uVar2 * 0x1c + 0x3f) = 0;
        param_1[uVar2 * 7 + 0x11] = 0;
        param_1[uVar2 * 7 + 0x12] = 0;
        param_1[uVar2 * 7 + 0x14] = 0;
      }
      for (uVar2 = 0; uVar2 < (uint)param_1[1]; uVar2 = uVar2 + 1 & 0xff) {
        *(undefined1 *)((int)param_1 + uVar2 * 0x1c + 0x1fd) = 0;
        *(char *)(param_1 + uVar2 * 7 + 0x7f) = (char)uVar2;
        *(undefined1 *)((int)param_1 + uVar2 * 0x1c + 0x1ff) = 0;
        param_1[uVar2 * 7 + 0x81] = 0;
        param_1[uVar2 * 7 + 0x82] = 0;
        param_1[uVar2 * 7 + 0x84] = 0;
      }
      FUN_08000240(auStack_38,param_1 + 4,0x28);
      iVar3 = FUN_08004bbc(*param_1,param_1[1],param_1[2],param_1[3]);
      if (iVar3 == 0) {
        *(undefined1 *)(param_1 + 0xe) = 0;
        *(undefined1 *)((int)param_1 + 0x3bd) = 1;
        FUN_08004b9c(*param_1);
        uVar1 = 0;
      }
      else {
        *(undefined1 *)((int)param_1 + 0x3bd) = 2;
        uVar1 = 1;
      }
    }
    else {
      *(undefined1 *)((int)param_1 + 0x3bd) = 2;
      uVar1 = 1;
    }
  }
  return uVar1;
}


// ===== FUN_08001bb8 @ 08001bb8

void FUN_08001bb8(int *param_1)

{
  if (*param_1 == 0x50000000) {
    *DAT_08001be4 = *DAT_08001be4 & 0xffffff7f;
    FUN_08000bd0(DAT_08001be8,0x1800);
    FUN_08001028(0x43);
  }
  return;
}


// ===== FUN_08001bec @ 08001bec

void FUN_08001bec(int *param_1)

{
  uint *puVar1;
  undefined4 extraout_r3;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 local_c;
  
  FUN_08000272(&local_1c,0x14);
  if (*param_1 == 0x50000000) {
    *DAT_08001c8c = *DAT_08001c8c | 1;
    local_1c = 0x1800;
    local_18 = 2;
    local_14 = 0;
    local_10 = 3;
    local_c = 10;
    FUN_08000d34(DAT_08001c90,&local_1c);
    DAT_08001c8c[1] = DAT_08001c8c[1] | 0x80;
    puVar1 = DAT_08001c8c + 5;
    *puVar1 = DAT_08001c8c[5] | 0x4000;
    FUN_0800108c(0x43,0,0,extraout_r3,*puVar1 & 0x4000);
    FUN_0800106c(0x43);
  }
  return;
}


// ===== FUN_08001c94 @ 08001c94

void FUN_08001c94(int param_1)

{
  undefined4 uVar1;
  
  uVar1 = 1;
  if (*(int *)(param_1 + 0xc) == 0) {
    uVar1 = 0;
  }
  else if (*(int *)(param_1 + 0xc) == 2) {
    uVar1 = 1;
  }
  else {
    FUN_080006a2();
  }
  FUN_080041d2(*(undefined4 *)(param_1 + 0x404),uVar1);
  FUN_08004140(*(undefined4 *)(param_1 + 0x404));
  return;
}


// ===== FUN_08001cc4 @ 08001cc4

void FUN_08001cc4(int param_1)

{
  FUN_0800419a(*(undefined4 *)(param_1 + 0x404));
  return;
}


// ===== FUN_08001cd2 @ 08001cd2

void FUN_08001cd2(int param_1)

{
  FUN_080041b0(*(undefined4 *)(param_1 + 0x404));
  return;
}


// ===== FUN_08001ce0 @ 08001ce0

undefined4 FUN_08001ce0(undefined4 *param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  if (*(char *)(param_1 + 0xef) == '\x01') {
    uVar1 = 2;
  }
  else {
    *(undefined1 *)(param_1 + 0xef) = 1;
    *(char *)(param_1 + 0xe) = (char)param_2;
    FUN_080056a6(*param_1,param_2);
    uVar1 = 0;
    *(undefined1 *)(param_1 + 0xef) = 0;
  }
  return uVar1;
}


// ===== FUN_08001d16 @ 08001d16

void FUN_08001d16(int param_1)

{
  FUN_08004200(*(undefined4 *)(param_1 + 0x404),param_1 + 0x3c4);
  return;
}


// ===== FUN_08001d28 @ 08001d28

undefined4 FUN_08001d28(int *param_1)

{
  undefined4 uVar1;
  
  if ((char)param_1[0xef] == '\x01') {
    uVar1 = 2;
  }
  else {
    *(undefined1 *)(param_1 + 0xef) = 1;
    if ((param_1[10] == 1) && (param_1[6] != 1)) {
      *(uint *)(*param_1 + 0x38) = *(uint *)(*param_1 + 0x38) | 0x10000;
    }
    FUN_08004b7c(*param_1);
    FUN_08005460(*param_1);
    uVar1 = 0;
    *(undefined1 *)(param_1 + 0xef) = 0;
  }
  return uVar1;
}


// ===== FUN_08001d72 @ 08001d72

undefined4 FUN_08001d72(undefined4 *param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  if (*(char *)(param_1 + 0xef) == '\x01') {
    uVar1 = 2;
  }
  else {
    *(undefined1 *)(param_1 + 0xef) = 1;
    FUN_08004d9c(*param_1);
    iVar2 = FUN_080057cc(*param_1);
    if (iVar2 == 0) {
      FUN_08004b9c(*param_1);
      uVar1 = 0;
      *(undefined1 *)(param_1 + 0xef) = 0;
    }
    else {
      *(undefined1 *)(param_1 + 0xef) = 0;
      uVar1 = 1;
    }
  }
  return uVar1;
}


// ===== FUN_08001dbc @ 08001dbc

void FUN_08001dbc(int *param_1)

{
  FUN_080042d8(param_1[0x101]);
  *(uint *)(*param_1 + 0xe00) = *(uint *)(*param_1 + 0xe00) | 1;
  if (param_1[8] != 0) {
    *DAT_08001dec = *DAT_08001dec | 6;
  }
  return;
}


// ===== FUN_08001df0 @ 08001df0

undefined4 FUN_08001df0(void)

{
  return *DAT_08001df8;
}


// ===== FUN_08001dfc @ 08001dfc

uint FUN_08001dfc(void)

{
  uint uVar1;
  
  uVar1 = FUN_08001df0();
  return uVar1 >> *(sbyte *)(DAT_08001e18 + ((*DAT_08001e14 & 0x1fff) >> 10));
}


// ===== FUN_08001e1c @ 08001e1c

uint FUN_08001e1c(void)

{
  uint uVar1;
  
  uVar1 = FUN_08001df0();
  return uVar1 >> *(sbyte *)(DAT_08001e38 + ((*DAT_08001e34 & 0xffff) >> 0xd));
}


// ===== FUN_08001e3c @ 08001e3c

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

bool FUN_08001e3c(int param_1)

{
  bool bVar1;
  
  bVar1 = param_1 - 1U < 0x1000000;
  if (bVar1) {
    _DAT_e000e014 = param_1 + -1;
    FUN_080058cc(0xffffffff,0xf);
    _DAT_e000e018 = 0;
    _DAT_e000e010 = 7;
  }
  return !bVar1;
}


// ===== FUN_08001e70 @ 08001e70

undefined4 FUN_08001e70(int *param_1)

{
  undefined4 uVar1;
  
  if (param_1 == (int *)0x0) {
    uVar1 = 1;
  }
  else {
    if (*(char *)((int)param_1 + 0x39) == '\0') {
      *(undefined1 *)(param_1 + 0xe) = 0;
      FUN_08001ee4(param_1);
    }
    *(undefined1 *)((int)param_1 + 0x39) = 0x24;
    *(uint *)(*param_1 + 0xc) = *(uint *)(*param_1 + 0xc) & 0xffffdfff;
    FUN_08002f64(param_1);
    *(uint *)(*param_1 + 0x10) = *(uint *)(*param_1 + 0x10) & 0xffffb7ff;
    *(uint *)(*param_1 + 0x14) = *(uint *)(*param_1 + 0x14) & 0xffffffd5;
    *(uint *)(*param_1 + 0xc) = *(uint *)(*param_1 + 0xc) | 0x2000;
    param_1[0xf] = 0;
    *(undefined1 *)((int)param_1 + 0x39) = 0x20;
    *(undefined1 *)((int)param_1 + 0x3a) = 0x20;
    uVar1 = 0;
  }
  return uVar1;
}


// ===== FUN_08001ee4 @ 08001ee4

void FUN_08001ee4(int *param_1)

{
  uint *puVar1;
  undefined4 extraout_r2;
  undefined4 extraout_r3;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 local_c;
  
  FUN_08000272(&local_1c,0x14);
  if (*param_1 == DAT_08001f60) {
    *DAT_08001f64 = *DAT_08001f64 | 0x80000;
    puVar1 = DAT_08001f64 + -4;
    *puVar1 = DAT_08001f64[-4] | 1;
    local_1c = 3;
    local_18 = 2;
    local_14 = 1;
    local_10 = 3;
    local_c = 8;
    FUN_08000d34(DAT_08001f68,&local_1c,extraout_r2,extraout_r3,*puVar1 & 1);
  }
  return;
}


// ===== thunk_FUN_08001f6e @ 08001f6c

void thunk_FUN_08001f6e(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}


// ===== FUN_08001f6e @ 08001f6e

void FUN_08001f6e(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}


// ===== FUN_08001f70 @ 08001f70

void FUN_08001f70(void)

{
  FUN_08002400(DAT_08001fb4,0x400);
  FUN_0800240a(DAT_08001fb4,0x800);
  FUN_08002400(DAT_08001fb4,0x800);
  FUN_0800595c(2);
  FUN_08002406(DAT_08001fb4,0x400);
  FUN_0800595c(4);
  FUN_08002400(DAT_08001fb4,0x400);
  return;
}


// ===== FUN_08001fb8 @ 08001fb8

void FUN_08001fb8(void)

{
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 local_c;
  
  FUN_08000272(&local_1c,0x18);
  local_1c = 0xc00;
  local_18 = 1;
  local_14 = 2;
  local_10 = 0;
  local_c = 1;
  FUN_080022b0(DAT_08001ffc,&local_1c);
  FUN_08002406(DAT_08001ffc,0x400);
  FUN_08002406(DAT_08001ffc,0x800);
  return;
}


// ===== FUN_08002000 @ 08002000

void FUN_08002000(void)

{
  FUN_08002400(DAT_08002044,0x400);
  FUN_0800240a(DAT_08002044,0x800);
  FUN_08002406(DAT_08002044,0x800);
  FUN_0800595c(2);
  FUN_08002406(DAT_08002044,0x400);
  FUN_0800595c(2);
  FUN_08002400(DAT_08002044,0x400);
  return;
}


// ===== FUN_08002048 @ 08002048

uint FUN_08002048(int param_1)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = 0;
  FUN_0800240a(DAT_080020b0,0x800,0);
  FUN_0800595c(3);
  for (iVar3 = 0; iVar3 < 8; iVar3 = iVar3 + 1) {
    FUN_08002400(DAT_080020b0,0x400);
    FUN_0800595c(3);
    FUN_08002406(DAT_080020b0,0x400);
    uVar2 = (uVar2 & 0x7f) * 2;
    iVar1 = FUN_080023e8(DAT_080020b0,0x800);
    if (iVar1 != 0) {
      uVar2 = uVar2 + 1;
    }
    FUN_0800595c(3);
  }
  if (param_1 == 0) {
    FUN_08002000();
  }
  else {
    FUN_08001f70();
  }
  return uVar2;
}


// ===== FUN_080020b4 @ 080020b4

void FUN_080020b4(uint param_1)

{
  int iVar1;
  
  FUN_0800240a(DAT_0800212c,0x800);
  FUN_0800595c(2);
  for (iVar1 = 0; iVar1 < 8; iVar1 = iVar1 + 1) {
    FUN_08002400(DAT_0800212c,0x400);
    FUN_0800595c(2);
    if ((param_1 & 0x80) == 0) {
      FUN_08002400(DAT_0800212c,0x800);
    }
    else {
      FUN_08002406(DAT_0800212c,0x800);
    }
    param_1 = (param_1 & 0x7f) << 1;
    FUN_0800595c(2);
    FUN_08002406(DAT_0800212c,0x400);
    FUN_0800595c(2);
  }
  FUN_08002400(DAT_0800212c,0x400);
  FUN_0800595c(2);
  return;
}


// ===== FUN_08002130 @ 08002130

void FUN_08002130(void)

{
  FUN_0800240a(DAT_08002178,0x800);
  FUN_08002406(DAT_08002178,0x800);
  FUN_0800595c(3);
  FUN_08002406(DAT_08002178,0x400);
  FUN_0800595c(6);
  FUN_08002400(DAT_08002178,0x800);
  FUN_0800595c(4);
  FUN_08002400(DAT_08002178,0x400);
  return;
}


// ===== FUN_0800217c @ 0800217c

void FUN_0800217c(void)

{
  FUN_0800240a(DAT_080021cc,0x800);
  FUN_08002400(DAT_080021cc,0x400);
  FUN_0800595c(2);
  FUN_08002400(DAT_080021cc,0x800);
  FUN_0800595c(2);
  FUN_08002406(DAT_080021cc,0x400);
  FUN_0800595c(2);
  FUN_08002406(DAT_080021cc,0x800);
  FUN_0800595c(4);
  return;
}


// ===== FUN_080021d0 @ 080021d0

undefined4 FUN_080021d0(void)

{
  byte bVar1;
  int iVar2;
  
  bVar1 = 0;
  FUN_0800240a(DAT_08002234,0x800,0);
  FUN_08002406(DAT_08002234,0x800);
  FUN_0800595c(2);
  FUN_08002406(DAT_08002234,0x400);
  FUN_0800595c(2);
  do {
    iVar2 = FUN_080023e8(DAT_08002234,0x800);
    if (iVar2 == 0) {
      FUN_0800595c(3);
      FUN_08002400(DAT_08002234,0x400);
      return 0;
    }
    bVar1 = bVar1 + 1;
  } while (bVar1 < 0xfb);
  FUN_0800217c();
  return 1;
}


// ===== FUN_08002238 @ 08002238

void FUN_08002238(uint param_1,int param_2,int param_3)

{
  byte bVar1;
  uint uVar2;
  
  for (uVar2 = 0; (int)uVar2 < param_3; uVar2 = uVar2 + 1 & 0xff) {
    bVar1 = (byte)(param_1 >> 0x18);
    if (param_1 >> 0x1c < 10) {
      *(byte *)(param_2 + uVar2 * 2) = (bVar1 >> 4) + 0x30;
    }
    else {
      *(byte *)(param_2 + uVar2 * 2) = (bVar1 >> 4) + 0x37;
    }
    param_1 = param_1 << 4;
    *(undefined1 *)(param_2 + uVar2 * 2 + 1) = 0;
  }
  return;
}


// ===== FUN_08002278 @ 08002278

void FUN_08002278(uint param_1)

{
  *DAT_08002290 = *DAT_08002290 | param_1;
  return;
}


// ===== FUN_08002294 @ 08002294

void FUN_08002294(uint param_1)

{
  *DAT_080022ac = *DAT_080022ac | param_1;
  return;
}


// ===== FUN_080022b0 @ 080022b0

void FUN_080022b0(uint *param_1,uint *param_2)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  uint uVar5;
  uint uVar6;
  
  uVar5 = *param_2;
  bVar2 = (byte)uVar5;
  bVar3 = (byte)(uVar5 >> 8);
  bVar4 = (byte)(uVar5 >> 0x10);
  bVar1 = (byte)(uVar5 >> 0x18);
  for (uVar5 = LZCOUNT((uint)(byte)((((((((bVar2 & 1) << 1 | bVar2 >> 1 & 1) << 1 | bVar2 >> 2 & 1)
                                        << 1 | bVar2 >> 3 & 1) << 1 | bVar2 >> 4 & 1) << 1 |
                                     bVar2 >> 5 & 1) << 1 | bVar2 >> 6 & 1) << 1 | bVar2 >> 7) <<
                       0x18 | (uint)(byte)((((((((bVar3 & 1) << 1 | bVar3 >> 1 & 1) << 1 |
                                               bVar3 >> 2 & 1) << 1 | bVar3 >> 3 & 1) << 1 |
                                             bVar3 >> 4 & 1) << 1 | bVar3 >> 5 & 1) << 1 |
                                           bVar3 >> 6 & 1) << 1 | bVar3 >> 7) << 0x10 |
                       (uint)(byte)((((((((bVar4 & 1) << 1 | bVar4 >> 1 & 1) << 1 | bVar4 >> 2 & 1)
                                        << 1 | bVar4 >> 3 & 1) << 1 | bVar4 >> 4 & 1) << 1 |
                                     bVar4 >> 5 & 1) << 1 | bVar4 >> 6 & 1) << 1 | bVar4 >> 7) << 8
                       | (uint)(byte)((((((((bVar1 & 1) << 1 | bVar1 >> 1 & 1) << 1 | bVar1 >> 2 & 1
                                          ) << 1 | bVar1 >> 3 & 1) << 1 | bVar1 >> 4 & 1) << 1 |
                                       bVar1 >> 5 & 1) << 1 | bVar1 >> 6 & 1) << 1 | bVar1 >> 7));
      *param_2 >> (uVar5 & 0xff) != 0; uVar5 = uVar5 + 1) {
    uVar6 = *param_2 & 1 << (uVar5 & 0xff);
    if (uVar6 != 0) {
      bVar1 = (byte)(uVar6 >> 0x18);
      bVar2 = (byte)uVar6;
      bVar3 = (byte)(uVar6 >> 8);
      bVar4 = (byte)(uVar6 >> 0x10);
      if ((param_2[1] == 1) || (param_2[1] == 2)) {
        param_1[2] = param_1[2] &
                     ~(3 << (LZCOUNT((uint)(byte)((((((((bVar2 & 1) << 1 | bVar2 >> 1 & 1) << 1 |
                                                      bVar2 >> 2 & 1) << 1 | bVar2 >> 3 & 1) << 1 |
                                                    bVar2 >> 4 & 1) << 1 | bVar2 >> 5 & 1) << 1 |
                                                  bVar2 >> 6 & 1) << 1 | bVar2 >> 7) << 0x18 |
                                     (uint)(byte)((((((((bVar3 & 1) << 1 | bVar3 >> 1 & 1) << 1 |
                                                      bVar3 >> 2 & 1) << 1 | bVar3 >> 3 & 1) << 1 |
                                                    bVar3 >> 4 & 1) << 1 | bVar3 >> 5 & 1) << 1 |
                                                  bVar3 >> 6 & 1) << 1 | bVar3 >> 7) << 0x10 |
                                     (uint)(byte)((((((((bVar4 & 1) << 1 | bVar4 >> 1 & 1) << 1 |
                                                      bVar4 >> 2 & 1) << 1 | bVar4 >> 3 & 1) << 1 |
                                                    bVar4 >> 4 & 1) << 1 | bVar4 >> 5 & 1) << 1 |
                                                  bVar4 >> 6 & 1) << 1 | bVar4 >> 7) << 8 |
                                     (uint)(byte)((((((((bVar1 & 1) << 1 | bVar1 >> 1 & 1) << 1 |
                                                      bVar1 >> 2 & 1) << 1 | bVar1 >> 3 & 1) << 1 |
                                                    bVar1 >> 4 & 1) << 1 | bVar1 >> 5 & 1) << 1 |
                                                  bVar1 >> 6 & 1) << 1 | bVar1 >> 7)) << 1)) |
                     param_2[2] <<
                     (LZCOUNT((uint)(byte)((((((((bVar2 & 1) << 1 | bVar2 >> 1 & 1) << 1 |
                                               bVar2 >> 2 & 1) << 1 | bVar2 >> 3 & 1) << 1 |
                                             bVar2 >> 4 & 1) << 1 | bVar2 >> 5 & 1) << 1 |
                                           bVar2 >> 6 & 1) << 1 | bVar2 >> 7) << 0x18 |
                              (uint)(byte)((((((((bVar3 & 1) << 1 | bVar3 >> 1 & 1) << 1 |
                                               bVar3 >> 2 & 1) << 1 | bVar3 >> 3 & 1) << 1 |
                                             bVar3 >> 4 & 1) << 1 | bVar3 >> 5 & 1) << 1 |
                                           bVar3 >> 6 & 1) << 1 | bVar3 >> 7) << 0x10 |
                              (uint)(byte)((((((((bVar4 & 1) << 1 | bVar4 >> 1 & 1) << 1 |
                                               bVar4 >> 2 & 1) << 1 | bVar4 >> 3 & 1) << 1 |
                                             bVar4 >> 4 & 1) << 1 | bVar4 >> 5 & 1) << 1 |
                                           bVar4 >> 6 & 1) << 1 | bVar4 >> 7) << 8 |
                              (uint)(byte)((((((((bVar1 & 1) << 1 | bVar1 >> 1 & 1) << 1 |
                                               bVar1 >> 2 & 1) << 1 | bVar1 >> 3 & 1) << 1 |
                                             bVar1 >> 4 & 1) << 1 | bVar1 >> 5 & 1) << 1 |
                                           bVar1 >> 6 & 1) << 1 | bVar1 >> 7)) << 1);
        param_1[1] = param_1[1] & ~uVar6 | uVar6 * param_2[3];
      }
      param_1[3] = param_1[3] &
                   ~(3 << (LZCOUNT((uint)(byte)((((((((bVar2 & 1) << 1 | bVar2 >> 1 & 1) << 1 |
                                                    bVar2 >> 2 & 1) << 1 | bVar2 >> 3 & 1) << 1 |
                                                  bVar2 >> 4 & 1) << 1 | bVar2 >> 5 & 1) << 1 |
                                                bVar2 >> 6 & 1) << 1 | bVar2 >> 7) << 0x18 |
                                   (uint)(byte)((((((((bVar3 & 1) << 1 | bVar3 >> 1 & 1) << 1 |
                                                    bVar3 >> 2 & 1) << 1 | bVar3 >> 3 & 1) << 1 |
                                                  bVar3 >> 4 & 1) << 1 | bVar3 >> 5 & 1) << 1 |
                                                bVar3 >> 6 & 1) << 1 | bVar3 >> 7) << 0x10 |
                                   (uint)(byte)((((((((bVar4 & 1) << 1 | bVar4 >> 1 & 1) << 1 |
                                                    bVar4 >> 2 & 1) << 1 | bVar4 >> 3 & 1) << 1 |
                                                  bVar4 >> 4 & 1) << 1 | bVar4 >> 5 & 1) << 1 |
                                                bVar4 >> 6 & 1) << 1 | bVar4 >> 7) << 8 |
                                   (uint)(byte)((((((((bVar1 & 1) << 1 | bVar1 >> 1 & 1) << 1 |
                                                    bVar1 >> 2 & 1) << 1 | bVar1 >> 3 & 1) << 1 |
                                                  bVar1 >> 4 & 1) << 1 | bVar1 >> 5 & 1) << 1 |
                                                bVar1 >> 6 & 1) << 1 | bVar1 >> 7)) << 1)) |
                   param_2[4] <<
                   (LZCOUNT((uint)(byte)((((((((bVar2 & 1) << 1 | bVar2 >> 1 & 1) << 1 |
                                             bVar2 >> 2 & 1) << 1 | bVar2 >> 3 & 1) << 1 |
                                           bVar2 >> 4 & 1) << 1 | bVar2 >> 5 & 1) << 1 |
                                         bVar2 >> 6 & 1) << 1 | bVar2 >> 7) << 0x18 |
                            (uint)(byte)((((((((bVar3 & 1) << 1 | bVar3 >> 1 & 1) << 1 |
                                             bVar3 >> 2 & 1) << 1 | bVar3 >> 3 & 1) << 1 |
                                           bVar3 >> 4 & 1) << 1 | bVar3 >> 5 & 1) << 1 |
                                         bVar3 >> 6 & 1) << 1 | bVar3 >> 7) << 0x10 |
                            (uint)(byte)((((((((bVar4 & 1) << 1 | bVar4 >> 1 & 1) << 1 |
                                             bVar4 >> 2 & 1) << 1 | bVar4 >> 3 & 1) << 1 |
                                           bVar4 >> 4 & 1) << 1 | bVar4 >> 5 & 1) << 1 |
                                         bVar4 >> 6 & 1) << 1 | bVar4 >> 7) << 8 |
                            (uint)(byte)((((((((bVar1 & 1) << 1 | bVar1 >> 1 & 1) << 1 |
                                             bVar1 >> 2 & 1) << 1 | bVar1 >> 3 & 1) << 1 |
                                           bVar1 >> 4 & 1) << 1 | bVar1 >> 5 & 1) << 1 |
                                         bVar1 >> 6 & 1) << 1 | bVar1 >> 7)) << 1);
      if (param_2[1] == 2) {
        if ((uint)LZCOUNT((uint)(byte)((((((((bVar2 & 1) << 1 | bVar2 >> 1 & 1) << 1 |
                                           bVar2 >> 2 & 1) << 1 | bVar2 >> 3 & 1) << 1 |
                                         bVar2 >> 4 & 1) << 1 | bVar2 >> 5 & 1) << 1 |
                                       bVar2 >> 6 & 1) << 1 | bVar2 >> 7) << 0x18 |
                          (uint)(byte)((((((((bVar3 & 1) << 1 | bVar3 >> 1 & 1) << 1 |
                                           bVar3 >> 2 & 1) << 1 | bVar3 >> 3 & 1) << 1 |
                                         bVar3 >> 4 & 1) << 1 | bVar3 >> 5 & 1) << 1 |
                                       bVar3 >> 6 & 1) << 1 | bVar3 >> 7) << 0x10 |
                          (uint)(byte)((((((((bVar4 & 1) << 1 | bVar4 >> 1 & 1) << 1 |
                                           bVar4 >> 2 & 1) << 1 | bVar4 >> 3 & 1) << 1 |
                                         bVar4 >> 4 & 1) << 1 | bVar4 >> 5 & 1) << 1 |
                                       bVar4 >> 6 & 1) << 1 | bVar4 >> 7) << 8 |
                          (uint)(byte)((((((((bVar1 & 1) << 1 | bVar1 >> 1 & 1) << 1 |
                                           bVar1 >> 2 & 1) << 1 | bVar1 >> 3 & 1) << 1 |
                                         bVar1 >> 4 & 1) << 1 | bVar1 >> 5 & 1) << 1 |
                                       bVar1 >> 6 & 1) << 1 | bVar1 >> 7)) < 8) {
          param_1[8] = param_1[8] &
                       ~(0xf << (LZCOUNT((uint)(byte)((((((((bVar2 & 1) << 1 | bVar2 >> 1 & 1) << 1
                                                          | bVar2 >> 2 & 1) << 1 | bVar2 >> 3 & 1)
                                                         << 1 | bVar2 >> 4 & 1) << 1 |
                                                       bVar2 >> 5 & 1) << 1 | bVar2 >> 6 & 1) << 1 |
                                                     bVar2 >> 7) << 0x18 |
                                         (uint)(byte)((((((((bVar3 & 1) << 1 | bVar3 >> 1 & 1) << 1
                                                          | bVar3 >> 2 & 1) << 1 | bVar3 >> 3 & 1)
                                                         << 1 | bVar3 >> 4 & 1) << 1 |
                                                       bVar3 >> 5 & 1) << 1 | bVar3 >> 6 & 1) << 1 |
                                                     bVar3 >> 7) << 0x10 |
                                         (uint)(byte)((((((((bVar4 & 1) << 1 | bVar4 >> 1 & 1) << 1
                                                          | bVar4 >> 2 & 1) << 1 | bVar4 >> 3 & 1)
                                                         << 1 | bVar4 >> 4 & 1) << 1 |
                                                       bVar4 >> 5 & 1) << 1 | bVar4 >> 6 & 1) << 1 |
                                                     bVar4 >> 7) << 8 |
                                         (uint)(byte)((((((((bVar1 & 1) << 1 | bVar1 >> 1 & 1) << 1
                                                          | bVar1 >> 2 & 1) << 1 | bVar1 >> 3 & 1)
                                                         << 1 | bVar1 >> 4 & 1) << 1 |
                                                       bVar1 >> 5 & 1) << 1 | bVar1 >> 6 & 1) << 1 |
                                                     bVar1 >> 7)) << 2)) |
                       param_2[5] <<
                       (LZCOUNT((uint)(byte)((((((((bVar2 & 1) << 1 | bVar2 >> 1 & 1) << 1 |
                                                 bVar2 >> 2 & 1) << 1 | bVar2 >> 3 & 1) << 1 |
                                               bVar2 >> 4 & 1) << 1 | bVar2 >> 5 & 1) << 1 |
                                             bVar2 >> 6 & 1) << 1 | bVar2 >> 7) << 0x18 |
                                (uint)(byte)((((((((bVar3 & 1) << 1 | bVar3 >> 1 & 1) << 1 |
                                                 bVar3 >> 2 & 1) << 1 | bVar3 >> 3 & 1) << 1 |
                                               bVar3 >> 4 & 1) << 1 | bVar3 >> 5 & 1) << 1 |
                                             bVar3 >> 6 & 1) << 1 | bVar3 >> 7) << 0x10 |
                                (uint)(byte)((((((((bVar4 & 1) << 1 | bVar4 >> 1 & 1) << 1 |
                                                 bVar4 >> 2 & 1) << 1 | bVar4 >> 3 & 1) << 1 |
                                               bVar4 >> 4 & 1) << 1 | bVar4 >> 5 & 1) << 1 |
                                             bVar4 >> 6 & 1) << 1 | bVar4 >> 7) << 8 |
                                (uint)(byte)((((((((bVar1 & 1) << 1 | bVar1 >> 1 & 1) << 1 |
                                                 bVar1 >> 2 & 1) << 1 | bVar1 >> 3 & 1) << 1 |
                                               bVar1 >> 4 & 1) << 1 | bVar1 >> 5 & 1) << 1 |
                                             bVar1 >> 6 & 1) << 1 | bVar1 >> 7)) << 2);
        }
        else {
          param_1[9] = param_1[9] &
                       ~(0xf << (LZCOUNT((uint)(byte)((((((((bVar3 & 1) << 1 | bVar3 >> 1 & 1) << 1
                                                          | bVar3 >> 2 & 1) << 1 | bVar3 >> 3 & 1)
                                                         << 1 | bVar3 >> 4 & 1) << 1 |
                                                       bVar3 >> 5 & 1) << 1 | bVar3 >> 6 & 1) << 1 |
                                                     bVar3 >> 7) << 0x18 |
                                         (uint)(byte)((((((((bVar4 & 1) << 1 | bVar4 >> 1 & 1) << 1
                                                          | bVar4 >> 2 & 1) << 1 | bVar4 >> 3 & 1)
                                                         << 1 | bVar4 >> 4 & 1) << 1 |
                                                       bVar4 >> 5 & 1) << 1 | bVar4 >> 6 & 1) << 1 |
                                                     bVar4 >> 7) << 0x10 |
                                         (uint)(byte)((((((((bVar1 & 1) << 1 | bVar1 >> 1 & 1) << 1
                                                          | bVar1 >> 2 & 1) << 1 | bVar1 >> 3 & 1)
                                                         << 1 | bVar1 >> 4 & 1) << 1 |
                                                       bVar1 >> 5 & 1) << 1 | bVar1 >> 6 & 1) << 1 |
                                                     bVar1 >> 7) << 8) << 2)) |
                       param_2[5] <<
                       (LZCOUNT((uint)(byte)((((((((bVar3 & 1) << 1 | bVar3 >> 1 & 1) << 1 |
                                                 bVar3 >> 2 & 1) << 1 | bVar3 >> 3 & 1) << 1 |
                                               bVar3 >> 4 & 1) << 1 | bVar3 >> 5 & 1) << 1 |
                                             bVar3 >> 6 & 1) << 1 | bVar3 >> 7) << 0x18 |
                                (uint)(byte)((((((((bVar4 & 1) << 1 | bVar4 >> 1 & 1) << 1 |
                                                 bVar4 >> 2 & 1) << 1 | bVar4 >> 3 & 1) << 1 |
                                               bVar4 >> 4 & 1) << 1 | bVar4 >> 5 & 1) << 1 |
                                             bVar4 >> 6 & 1) << 1 | bVar4 >> 7) << 0x10 |
                                (uint)(byte)((((((((bVar1 & 1) << 1 | bVar1 >> 1 & 1) << 1 |
                                                 bVar1 >> 2 & 1) << 1 | bVar1 >> 3 & 1) << 1 |
                                               bVar1 >> 4 & 1) << 1 | bVar1 >> 5 & 1) << 1 |
                                             bVar1 >> 6 & 1) << 1 | bVar1 >> 7) << 8) << 2);
        }
      }
      *param_1 = *param_1 &
                 ~(3 << (LZCOUNT((uint)(byte)((((((((bVar2 & 1) << 1 | bVar2 >> 1 & 1) << 1 |
                                                  bVar2 >> 2 & 1) << 1 | bVar2 >> 3 & 1) << 1 |
                                                bVar2 >> 4 & 1) << 1 | bVar2 >> 5 & 1) << 1 |
                                              bVar2 >> 6 & 1) << 1 | bVar2 >> 7) << 0x18 |
                                 (uint)(byte)((((((((bVar3 & 1) << 1 | bVar3 >> 1 & 1) << 1 |
                                                  bVar3 >> 2 & 1) << 1 | bVar3 >> 3 & 1) << 1 |
                                                bVar3 >> 4 & 1) << 1 | bVar3 >> 5 & 1) << 1 |
                                              bVar3 >> 6 & 1) << 1 | bVar3 >> 7) << 0x10 |
                                 (uint)(byte)((((((((bVar4 & 1) << 1 | bVar4 >> 1 & 1) << 1 |
                                                  bVar4 >> 2 & 1) << 1 | bVar4 >> 3 & 1) << 1 |
                                                bVar4 >> 4 & 1) << 1 | bVar4 >> 5 & 1) << 1 |
                                              bVar4 >> 6 & 1) << 1 | bVar4 >> 7) << 8 |
                                 (uint)(byte)((((((((bVar1 & 1) << 1 | bVar1 >> 1 & 1) << 1 |
                                                  bVar1 >> 2 & 1) << 1 | bVar1 >> 3 & 1) << 1 |
                                                bVar1 >> 4 & 1) << 1 | bVar1 >> 5 & 1) << 1 |
                                              bVar1 >> 6 & 1) << 1 | bVar1 >> 7)) << 1)) |
                 param_2[1] <<
                 (LZCOUNT((uint)(byte)((((((((bVar2 & 1) << 1 | bVar2 >> 1 & 1) << 1 |
                                           bVar2 >> 2 & 1) << 1 | bVar2 >> 3 & 1) << 1 |
                                         bVar2 >> 4 & 1) << 1 | bVar2 >> 5 & 1) << 1 |
                                       bVar2 >> 6 & 1) << 1 | bVar2 >> 7) << 0x18 |
                          (uint)(byte)((((((((bVar3 & 1) << 1 | bVar3 >> 1 & 1) << 1 |
                                           bVar3 >> 2 & 1) << 1 | bVar3 >> 3 & 1) << 1 |
                                         bVar3 >> 4 & 1) << 1 | bVar3 >> 5 & 1) << 1 |
                                       bVar3 >> 6 & 1) << 1 | bVar3 >> 7) << 0x10 |
                          (uint)(byte)((((((((bVar4 & 1) << 1 | bVar4 >> 1 & 1) << 1 |
                                           bVar4 >> 2 & 1) << 1 | bVar4 >> 3 & 1) << 1 |
                                         bVar4 >> 4 & 1) << 1 | bVar4 >> 5 & 1) << 1 |
                                       bVar4 >> 6 & 1) << 1 | bVar4 >> 7) << 8 |
                          (uint)(byte)((((((((bVar1 & 1) << 1 | bVar1 >> 1 & 1) << 1 |
                                           bVar1 >> 2 & 1) << 1 | bVar1 >> 3 & 1) << 1 |
                                         bVar1 >> 4 & 1) << 1 | bVar1 >> 5 & 1) << 1 |
                                       bVar1 >> 6 & 1) << 1 | bVar1 >> 7)) << 1);
    }
  }
  return;
}


// ===== FUN_080023e8 @ 080023e8

bool FUN_080023e8(int param_1,uint param_2)

{
  return (*(uint *)(param_1 + 0x10) & param_2) == param_2;
}


// ===== FUN_080023fa @ 080023fa

void FUN_080023fa(int param_1,int param_2)

{
  *(int *)(param_1 + 0x18) = param_2 << 0x10;
  return;
}


// ===== FUN_08002400 @ 08002400

void FUN_08002400(int param_1,int param_2)

{
  *(int *)(param_1 + 0x18) = param_2 << 0x10;
  return;
}


// ===== FUN_08002406 @ 08002406

void FUN_08002406(int param_1,undefined4 param_2)

{
  *(undefined4 *)(param_1 + 0x18) = param_2;
  return;
}


// ===== FUN_0800240a @ 0800240a

void FUN_0800240a(uint *param_1,undefined4 param_2,int param_3)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  
  bVar2 = (byte)param_2;
  bVar3 = (byte)((uint)param_2 >> 8);
  bVar4 = (byte)((uint)param_2 >> 0x10);
  bVar1 = (byte)((uint)param_2 >> 0x18);
  *param_1 = *param_1 &
             ~(3 << (LZCOUNT((uint)(byte)((((((((bVar2 & 1) << 1 | bVar2 >> 1 & 1) << 1 |
                                              bVar2 >> 2 & 1) << 1 | bVar2 >> 3 & 1) << 1 |
                                            bVar2 >> 4 & 1) << 1 | bVar2 >> 5 & 1) << 1 |
                                          bVar2 >> 6 & 1) << 1 | bVar2 >> 7) << 0x18 |
                             (uint)(byte)((((((((bVar3 & 1) << 1 | bVar3 >> 1 & 1) << 1 |
                                              bVar3 >> 2 & 1) << 1 | bVar3 >> 3 & 1) << 1 |
                                            bVar3 >> 4 & 1) << 1 | bVar3 >> 5 & 1) << 1 |
                                          bVar3 >> 6 & 1) << 1 | bVar3 >> 7) << 0x10 |
                             (uint)(byte)((((((((bVar4 & 1) << 1 | bVar4 >> 1 & 1) << 1 |
                                              bVar4 >> 2 & 1) << 1 | bVar4 >> 3 & 1) << 1 |
                                            bVar4 >> 4 & 1) << 1 | bVar4 >> 5 & 1) << 1 |
                                          bVar4 >> 6 & 1) << 1 | bVar4 >> 7) << 8 |
                             (uint)(byte)((((((((bVar1 & 1) << 1 | bVar1 >> 1 & 1) << 1 |
                                              bVar1 >> 2 & 1) << 1 | bVar1 >> 3 & 1) << 1 |
                                            bVar1 >> 4 & 1) << 1 | bVar1 >> 5 & 1) << 1 |
                                          bVar1 >> 6 & 1) << 1 | bVar1 >> 7)) << 1)) |
             param_3 <<
             (LZCOUNT((uint)(byte)((((((((bVar2 & 1) << 1 | bVar2 >> 1 & 1) << 1 | bVar2 >> 2 & 1)
                                       << 1 | bVar2 >> 3 & 1) << 1 | bVar2 >> 4 & 1) << 1 |
                                    bVar2 >> 5 & 1) << 1 | bVar2 >> 6 & 1) << 1 | bVar2 >> 7) <<
                      0x18 | (uint)(byte)((((((((bVar3 & 1) << 1 | bVar3 >> 1 & 1) << 1 |
                                              bVar3 >> 2 & 1) << 1 | bVar3 >> 3 & 1) << 1 |
                                            bVar3 >> 4 & 1) << 1 | bVar3 >> 5 & 1) << 1 |
                                          bVar3 >> 6 & 1) << 1 | bVar3 >> 7) << 0x10 |
                      (uint)(byte)((((((((bVar4 & 1) << 1 | bVar4 >> 1 & 1) << 1 | bVar4 >> 2 & 1)
                                       << 1 | bVar4 >> 3 & 1) << 1 | bVar4 >> 4 & 1) << 1 |
                                    bVar4 >> 5 & 1) << 1 | bVar4 >> 6 & 1) << 1 | bVar4 >> 7) << 8 |
                      (uint)(byte)((((((((bVar1 & 1) << 1 | bVar1 >> 1 & 1) << 1 | bVar1 >> 2 & 1)
                                       << 1 | bVar1 >> 3 & 1) << 1 | bVar1 >> 4 & 1) << 1 |
                                    bVar1 >> 5 & 1) << 1 | bVar1 >> 6 & 1) << 1 | bVar1 >> 7)) << 1)
  ;
  return;
}


// ===== FUN_08002432 @ 08002432

void FUN_08002432(undefined4 *param_1)

{
  undefined4 uVar1;
  
  uVar1 = FUN_08002d24();
  *param_1 = uVar1;
  uVar1 = FUN_08002cbc(*param_1);
  param_1[1] = uVar1;
  uVar1 = FUN_08002cdc(param_1[1]);
  param_1[2] = uVar1;
  uVar1 = FUN_08002d00(param_1[1]);
  param_1[3] = uVar1;
  return;
}


// ===== FUN_08002458 @ 08002458

uint FUN_08002458(void)

{
  return (*DAT_08002464 & 0x7fff) >> 6;
}


// ===== FUN_08002468 @ 08002468

void FUN_08002468(undefined4 param_1)

{
  *DAT_08002470 = param_1;
  return;
}


// ===== FUN_08002474 @ 08002474

void FUN_08002474(int param_1)

{
  *(uint *)(param_1 + 0x10) = *(uint *)(param_1 + 0x10) & 0xffffb7ff;
  *(uint *)(param_1 + 0x14) = *(uint *)(param_1 + 0x14) & 0xffffffd5;
  return;
}


// ===== FUN_08002486 @ 08002486

void FUN_08002486(int param_1)

{
  *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) | 0x2000;
  return;
}


// ===== FUN_08002490 @ 08002490

undefined4 FUN_08002490(int param_1,int *param_2,int param_3,int param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iStack_28;
  int *piStack_24;
  int local_20;
  int local_1c;
  
  uVar3 = 1;
  iVar2 = 0;
  iStack_28 = param_1;
  piStack_24 = param_2;
  local_20 = param_3;
  local_1c = param_4;
  iVar1 = FUN_08002554(param_1);
  if (iVar1 == 0) {
    *(uint *)(param_1 + 0xc) =
         param_2[1] | param_2[3] | param_2[4] | param_2[6] | *(uint *)(param_1 + 0xc) & 0xffff69f3;
    *(uint *)(param_1 + 0x10) = *(uint *)(param_1 + 0x10) & 0xffffcfff | param_2[2];
    *(uint *)(param_1 + 0x14) = *(uint *)(param_1 + 0x14) & 0xfffffcff | param_2[5];
    FUN_08002432(&iStack_28);
    if (param_1 == DAT_0800253c) {
      iVar2 = local_1c;
    }
    else if (param_1 == DAT_08002540) {
      iVar2 = local_20;
    }
    else if (param_1 == DAT_08002544) {
      iVar2 = local_20;
    }
    else if (param_1 == DAT_08002548) {
      iVar2 = local_1c;
    }
    else if (param_1 == DAT_0800254c) {
      iVar2 = local_20;
    }
    else if (param_1 == DAT_08002550) {
      iVar2 = local_20;
    }
    if ((iVar2 != 0) && (*param_2 != 0)) {
      uVar3 = 0;
      FUN_0800255e(param_1,iVar2,param_2[6],*param_2);
    }
  }
  return uVar3;
}


// ===== FUN_08002554 @ 08002554

uint FUN_08002554(int param_1)

{
  return (*(uint *)(param_1 + 0xc) & 0x3fff) >> 0xd;
}


// ===== FUN_0800255e @ 0800255e

void FUN_0800255e(int param_1,uint param_2,int param_3,uint param_4)

{
  longlong lVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  
  if (param_3 == 0x8000) {
    uVar2 = FUN_080001c8((int)((ulonglong)param_2 * 0x19),(int)((ulonglong)param_2 * 0x19 >> 0x20),
                         (int)((ulonglong)param_4 * 2),(int)((ulonglong)param_4 * 2 >> 0x20),0x8000,
                         param_4);
    iVar3 = FUN_080001c8((int)((ulonglong)param_2 * 0x19),(int)((ulonglong)param_2 * 0x19 >> 0x20),
                         (int)((ulonglong)param_4 * 2),(int)((ulonglong)param_4 * 2 >> 0x20));
    lVar1 = (ulonglong)param_2 * 0x19;
    uVar4 = FUN_080001c8((int)lVar1,(int)((ulonglong)lVar1 >> 0x20),(int)((ulonglong)param_4 * 2),
                         (int)((ulonglong)param_4 * 2 >> 0x20),lVar1);
    iVar5 = FUN_080001c8((int)((ulonglong)param_2 * 0x19),(int)((ulonglong)param_2 * 0x19 >> 0x20),
                         (int)((ulonglong)param_4 * 2),(int)((ulonglong)param_4 * 2 >> 0x20));
    lVar1 = (ulonglong)param_2 * 0x19;
    uVar6 = FUN_080001c8((int)lVar1,(int)((ulonglong)lVar1 >> 0x20),(int)((ulonglong)param_4 * 2),
                         (int)((ulonglong)param_4 * 2 >> 0x20),lVar1);
    *(uint *)(param_1 + 8) =
         (((iVar5 + (uVar6 / 100) * -100) * 8 + 0x32) / 100 & 7) +
         (uVar2 / 100) * 0x10 + (((iVar3 + (uVar4 / 100) * -100) * 8 + 0x32) / 100 & 0xf8) * 2 &
         0xffff;
  }
  else {
    iVar3 = FUN_080001c8((int)((ulonglong)param_2 * 0x19),(int)((ulonglong)param_2 * 0x19 >> 0x20),
                         (int)((ulonglong)param_4 * 4),(int)((ulonglong)param_4 * 4 >> 0x20),param_3
                         ,param_4);
    uVar2 = FUN_080001c8((int)((ulonglong)param_2 * 0x19),(int)((ulonglong)param_2 * 0x19 >> 0x20),
                         (int)((ulonglong)param_4 * 4),(int)((ulonglong)param_4 * 4 >> 0x20));
    uVar4 = FUN_080001c8((int)((ulonglong)param_2 * 0x19),(int)((ulonglong)param_2 * 0x19 >> 0x20),
                         (int)((ulonglong)param_4 * 4),(int)((ulonglong)param_4 * 4 >> 0x20));
    iVar5 = FUN_080001c8((int)((ulonglong)param_2 * 0x19),(int)((ulonglong)param_2 * 0x19 >> 0x20),
                         (int)((ulonglong)param_4 * 4),(int)((ulonglong)param_4 * 4 >> 0x20));
    lVar1 = (ulonglong)param_2 * 0x19;
    uVar6 = FUN_080001c8((int)lVar1,(int)((ulonglong)lVar1 >> 0x20),(int)((ulonglong)param_4 * 4),
                         (int)((ulonglong)param_4 * 4 >> 0x20),lVar1);
    *(uint *)(param_1 + 8) =
         (((iVar5 + (uVar6 / 100) * -100) * 0x10 + 0x32) / 100 & 0xf) +
         (((iVar3 + (uVar2 / 100) * -100) * 0x10 + 0x32) / 100 & 0xf0) + (uVar4 / 100) * 0x10 &
         0xffff;
  }
  return;
}


// ===== FUN_08002718 @ 08002718

void FUN_08002718(void)

{
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 local_c;
  
  FUN_08000272(&local_1c,0x18);
  FUN_08002278(0x10);
  FUN_08002278(0x80);
  FUN_08002278(4);
  FUN_08002278(1);
  FUN_08002278(2);
  FUN_08002278(8);
  FUN_080023fa(DAT_080027cc,0xc6);
  FUN_080023fa(DAT_080027d0,0xc0);
  local_1c = 0x18;
  local_18 = 0;
  local_c = 0;
  FUN_080022b0(DAT_080027d4,&local_1c);
  local_1c = 0xc6;
  local_18 = 1;
  local_14 = 0;
  local_10 = 0;
  local_c = 0;
  FUN_080022b0(DAT_080027cc,&local_1c);
  local_1c = 0xc0;
  local_18 = 1;
  local_14 = 0;
  local_10 = 0;
  local_c = 0;
  FUN_080022b0(DAT_080027d0,&local_1c);
  local_1c = 0x800;
  local_18 = 0;
  local_c = 0;
  FUN_080022b0(DAT_080027d8,&local_1c);
  local_1c = 1;
  local_18 = 1;
  local_c = 2;
  FUN_080022b0(DAT_080027dc,&local_1c);
  *(undefined4 *)(DAT_080027dc + 0x18) = 1;
  return;
}


// ===== FUN_080027e0 @ 080027e0

void FUN_080027e0(void)

{
  undefined4 *puVar1;
  int iVar2;
  
  puVar1 = DAT_08002814;
  *DAT_08002814 = DAT_08002810;
  puVar1[1] = 0x1c200;
  puVar1 = DAT_08002814;
  DAT_08002814[2] = 0;
  puVar1[3] = 0;
  puVar1[4] = 0;
  puVar1[5] = 0xc;
  puVar1[6] = 0;
  puVar1[7] = 0;
  iVar2 = FUN_08001e70();
  if (iVar2 != 0) {
    FUN_080006a2();
  }
  return;
}


// ===== FUN_08002818 @ 08002818

void FUN_08002818(void)

{
  undefined4 uVar1;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  
  FUN_08000272(&local_28,0x1c);
  FUN_08000272(&local_40,0x18);
  *DAT_080028b8 = *DAT_080028b8 | 0x10;
  FUN_08002294(1);
  local_40 = 0x600;
  local_3c = 2;
  local_38 = 3;
  local_34 = 0;
  local_30 = 0;
  local_2c = 7;
  FUN_080022b0(DAT_080028bc,&local_40);
  uVar1 = FUN_08005884();
  uVar1 = FUN_080029d2(uVar1,0);
  FUN_080058a4(0x25,uVar1);
  FUN_08005868(0x25);
  local_28 = 0x1c200;
  local_24 = 0;
  local_20 = 0;
  local_1c = 0;
  local_18 = 0xc;
  local_14 = 0;
  local_10 = 0;
  FUN_08002490(DAT_080028c0,&local_28);
  FUN_08002474(DAT_080028c0);
  FUN_08002486(DAT_080028c0);
  return;
}


// ===== FUN_080028c4 @ 080028c4

void FUN_080028c4(void)

{
  undefined4 uVar1;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  
  FUN_08000272(&local_28,0x1c);
  FUN_08000272(&local_40,0x18);
  *DAT_08002974 = *DAT_08002974 | 0x20000;
  FUN_08002294(8);
  local_40 = 0x60;
  local_3c = 2;
  local_38 = 3;
  local_34 = 0;
  local_30 = 0;
  local_2c = 7;
  FUN_080022b0(DAT_08002978,&local_40);
  uVar1 = FUN_08005884();
  uVar1 = FUN_080029d2(uVar1,0);
  FUN_080058a4(0x26,uVar1);
  FUN_08005868(0x26);
  local_28 = 0x1c200;
  local_24 = 0;
  local_20 = 0;
  local_1c = 0;
  local_18 = 0xc;
  local_14 = 0;
  local_10 = 0;
  FUN_08002490(DAT_0800297c,&local_28);
  FUN_08002474(DAT_0800297c);
  FUN_08002486(DAT_0800297c);
  *(uint *)(DAT_0800297c + 0xc) = *(uint *)(DAT_0800297c + 0xc) | 0x20;
  return;
}


// ===== FUN_08002980 @ 08002980

void FUN_08002980(void)

{
  int iVar1;
  
  iVar1 = FUN_08003dd6(DAT_080029c0,DAT_080029bc,0);
  if (iVar1 != 0) {
    FUN_080006a2();
  }
  iVar1 = FUN_08004352(DAT_080029c0,DAT_080029c4);
  if (iVar1 != 0) {
    FUN_080006a2();
  }
  iVar1 = FUN_080036ba(DAT_080029c0,DAT_080029c8);
  if (iVar1 != 0) {
    FUN_080006a2();
  }
  iVar1 = FUN_0800450c(DAT_080029c0);
  if (iVar1 != 0) {
    FUN_080006a2();
  }
  return;
}


// ===== thunk_FUN_080029ce @ 080029cc

void thunk_FUN_080029ce(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}


// ===== FUN_080029ce @ 080029ce

void FUN_080029ce(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}


// ===== FUN_080029d0 @ 080029d0

void FUN_080029d0(void)

{
  return;
}


// ===== FUN_080029d2 @ 080029d2

uint FUN_080029d2(uint param_1,uint param_2,uint param_3)

{
  uint uVar1;
  
  param_1 = param_1 & 7;
  if (7 - param_1 < 5) {
    uVar1 = 7 - param_1;
  }
  else {
    uVar1 = 4;
  }
  if (param_1 + 4 < 7) {
    param_1 = 0;
  }
  else {
    param_1 = param_1 - 3;
  }
  return ((1 << (uVar1 & 0xff)) - 1U & param_2) << (param_1 & 0xff) |
         (1 << (param_1 & 0xff)) - 1U & param_3;
}


// ===== FUN_08002a14 @ 08002a14

void FUN_08002a14(void)

{
  FUN_080014d0(DAT_08002a20);
  return;
}


// ===== FUN_08002a24 @ 08002a24

undefined4 FUN_08002a24(int *param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = *param_1;
  uVar2 = *(uint *)(iVar1 + 0x40);
  if ((DAT_08002a84 < uVar2) && ((*(uint *)(iVar1 + param_2 * 0x20 + 0xb08) & 0x8000) == 0x8000)) {
    *(undefined4 *)(iVar1 + param_2 * 0x20 + 0xb08) = 0x8000;
  }
  FUN_08001d16(param_1);
  if ((DAT_08002a84 < uVar2) && (param_1[4] == 1)) {
    FUN_08004f84(*param_1,1,param_1 + 0xf1);
  }
  return 0;
}


// ===== FUN_08002a88 @ 08002a88

undefined4 FUN_08002a88(int *param_1,uint param_2)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = *param_1;
  uVar3 = *(uint *)(iVar2 + 0x40);
  uVar1 = *(uint *)(iVar2 + param_2 * 0x20 + 0xb08);
  if (param_1[4] == 1) {
    if ((uVar1 & 8) == 8) {
      if ((DAT_08002bfc < uVar3) && ((uVar1 & 0x8000) == 0x8000)) {
        *(undefined4 *)(iVar2 + param_2 * 0x20 + 0xb08) = 0x8000;
      }
    }
    else if ((uVar1 & 0x20) == 0x20) {
      *(undefined4 *)(iVar2 + param_2 * 0x20 + 0xb08) = 0x20;
    }
    else if ((uVar1 & 0x28) == 0) {
      if ((DAT_08002bfc < uVar3) && ((uVar1 & 0x8000) == 0x8000)) {
        *(undefined4 *)(iVar2 + param_2 * 0x20 + 0xb08) = 0x8000;
      }
      else {
        param_1[param_2 * 7 + 0x85] =
             param_1[param_2 * 7 + 0x81] - (*(uint *)(iVar2 + param_2 * 0x20 + 0xb10) & 0x7ffff);
        param_1[param_2 * 7 + 0x82] = param_1[param_2 * 7 + 0x82] + param_1[param_2 * 7 + 0x81];
        if ((param_2 == 0) && (param_1[0x84] == 0)) {
          FUN_08004f84(*param_1,1,param_1 + 0xf1);
        }
        FUN_080011b8(param_1,param_2 & 0xff);
      }
    }
  }
  else if (uVar3 == DAT_08002c00) {
    if ((uVar1 & 0x8000) == 0x8000) {
      *(undefined4 *)(iVar2 + param_2 * 0x20 + 0xb08) = 0x8000;
    }
    else {
      if ((uVar1 & 0x20) == 0x20) {
        *(undefined4 *)(iVar2 + param_2 * 0x20 + 0xb08) = 0x20;
      }
      FUN_080011b8(param_1,param_2 & 0xff);
    }
  }
  else {
    if ((param_2 == 0) && (param_1[0x84] == 0)) {
      FUN_08004f84(*param_1,0,param_1 + 0xf1);
    }
    FUN_080011b8(param_1,param_2 & 0xff);
  }
  return 0;
}


// ===== FUN_08002c04 @ 08002c04

undefined4 FUN_08002c04(int *param_1,uint param_2)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  
  iVar3 = *param_1;
  if ((uint)param_1[param_2 * 7 + 0x14] < (uint)param_1[param_2 * 7 + 0x15]) {
    uVar1 = 1;
  }
  else {
    uVar2 = param_1[param_2 * 7 + 0x14] - param_1[param_2 * 7 + 0x15];
    if ((uint)param_1[param_2 * 7 + 0x11] < uVar2) {
      uVar2 = param_1[param_2 * 7 + 0x11];
    }
    while (((uVar2 + 3 >> 2 <= (*(uint *)(iVar3 + param_2 * 0x20 + 0x918) & 0xffff) &&
            ((uint)param_1[param_2 * 7 + 0x15] < (uint)param_1[param_2 * 7 + 0x14])) &&
           (param_1[param_2 * 7 + 0x14] != 0))) {
      uVar2 = param_1[param_2 * 7 + 0x14] - param_1[param_2 * 7 + 0x15];
      if ((uint)param_1[param_2 * 7 + 0x11] < uVar2) {
        uVar2 = param_1[param_2 * 7 + 0x11];
      }
      FUN_08005828(iVar3,param_1[param_2 * 7 + 0x12],param_2 & 0xff,uVar2 & 0xffff,(char)param_1[4])
      ;
      param_1[param_2 * 7 + 0x12] = param_1[param_2 * 7 + 0x12] + uVar2;
      param_1[param_2 * 7 + 0x15] = param_1[param_2 * 7 + 0x15] + uVar2;
    }
    if ((uint)param_1[param_2 * 7 + 0x14] <= (uint)param_1[param_2 * 7 + 0x15]) {
      *(uint *)(iVar3 + 0x834) = *(uint *)(iVar3 + 0x834) & ~(1 << (param_2 & 0xf));
    }
    uVar1 = 0;
  }
  return uVar1;
}


// ===== FUN_08002cba @ 08002cba

void FUN_08002cba(void)

{
  return;
}


// ===== FUN_08002cbc @ 08002cbc

uint FUN_08002cbc(uint param_1)

{
  return param_1 >> *(sbyte *)(DAT_08002cd8 + ((*DAT_08002cd4 & 0xf0) >> 4));
}


// ===== FUN_08002cdc @ 08002cdc

uint FUN_08002cdc(uint param_1)

{
  return param_1 >> *(sbyte *)(DAT_08002cfc + ((*DAT_08002cf8 & 0x1c00) >> 10));
}


// ===== FUN_08002d00 @ 08002d00

uint FUN_08002d00(uint param_1)

{
  return param_1 >> *(sbyte *)(DAT_08002d20 + ((*DAT_08002d1c & 0xe000) >> 0xd));
}


// ===== FUN_08002d24 @ 08002d24

undefined4 FUN_08002d24(void)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = *DAT_08002d5c & 0xc;
  uVar2 = DAT_08002d60;
  if (uVar1 != 0) {
    if (uVar1 == 4) {
      uVar2 = DAT_08002d64;
    }
    else if (uVar1 == 8) {
      uVar2 = FUN_08002d68(8);
    }
  }
  return uVar2;
}


// ===== FUN_08002d68 @ 08002d68

uint FUN_08002d68(int param_1)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = 0;
  uVar2 = DAT_08002dd0;
  if (((*DAT_08002dcc & 0x400000) != 0) && ((*DAT_08002dcc & 0x400000) == 0x400000)) {
    uVar2 = DAT_08002dd4;
  }
  if (param_1 == 8) {
    uVar3 = *DAT_08002dcc;
    iVar1 = FUN_08002458();
    uVar3 = ((uVar2 / (uVar3 & 0x3f)) * iVar1) / ((((*DAT_08002dcc & 0x30000) >> 0x10) + 1) * 2);
  }
  return uVar3;
}


// ===== FUN_08002dd8 @ 08002dd8

void FUN_08002dd8(void)

{
  return;
}


// ===== FUN_08002dda @ 08002dda

undefined2 FUN_08002dda(undefined2 *param_1)

{
  return *param_1;
}


// ===== FUN_08002dec @ 08002dec

void FUN_08002dec(void)

{
  FUN_08000f40();
  return;
}


// ===== FUN_08002df4 @ 08002df4

void FUN_08002df4(void)

{
  int iVar1;
  uint *puVar2;
  uint *puVar3;
  
  puVar2 = DAT_08002f30;
  *DAT_08002f30 = *DAT_08002f30 & 0xfffffff0 | 5;
  if ((*puVar2 & 0xf) != 5) {
    FUN_080006a2();
  }
  *DAT_08002f34 = *DAT_08002f34 & 0xffffbfff | 0x4000;
  *DAT_08002f38 = *DAT_08002f38 | 0x10000;
  do {
  } while (-1 < (int)(*DAT_08002f38 << 0xe));
  puVar3 = DAT_08002f38 + 1;
  *puVar3 = DAT_08002f38[1] & DAT_08002f3c | 0x402a04;
  *puVar3 = *puVar3 & 0xfffcffff;
  puVar2 = DAT_08002f38;
  DAT_08002f38[1] = *puVar3 & DAT_08002f40 | 0x7402a04;
  *puVar2 = *puVar2 | 0x1000000;
  do {
  } while (-1 < (int)(*DAT_08002f38 << 6));
  puVar2 = DAT_08002f38 + 2;
  *puVar2 = DAT_08002f38[2] & 0xffffff0f;
  *puVar2 = *puVar2 & 0xffffe3ff | 0x1400;
  *puVar2 = *puVar2 & 0xffff1fff | 0x8000;
  *puVar2 = *puVar2 & 0xfffffffc | 2;
  do {
  } while ((DAT_08002f38[2] & 0xc) != 8);
  FUN_08002468(DAT_08002f44);
  iVar1 = FUN_08000f94(0);
  if (iVar1 != 0) {
    FUN_080006a2();
  }
  return;
}


// ===== FUN_08002f48 @ 08002f48

void FUN_08002f48(void)

{
  *DAT_08002f60 = *DAT_08002f60 | 0xf00000;
  DAT_08002f60[-0x20] = 0x8000000;
  return;
}


// ===== FUN_08002f64 @ 08002f64

void FUN_08002f64(int *param_1)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  
  *(uint *)(*param_1 + 0x10) = *(uint *)(*param_1 + 0x10) & 0xffffcfff | param_1[3];
  *(uint *)(*param_1 + 0xc) =
       *(uint *)(*param_1 + 0xc) & 0xffff69f3 | param_1[2] | param_1[4] | param_1[5] | param_1[7];
  *(uint *)(*param_1 + 0x14) = *(uint *)(*param_1 + 0x14) & 0xfffffcff | param_1[6];
  if (param_1[7] == 0x8000) {
    if ((*param_1 != DAT_08003344) && (*param_1 != DAT_08003348)) {
      uVar1 = FUN_08001dfc();
      uVar2 = FUN_080001c8((int)((ulonglong)uVar1 * 0x19),(int)((ulonglong)uVar1 * 0x19 >> 0x20),
                           (int)((ulonglong)(uint)param_1[1] * 2),
                           (int)((ulonglong)(uint)param_1[1] * 2 >> 0x20));
      iVar3 = FUN_080001c8((int)((ulonglong)uVar1 * 0x19),(int)((ulonglong)uVar1 * 0x19 >> 0x20),
                           (int)((ulonglong)(uint)param_1[1] * 2),
                           (int)((ulonglong)(uint)param_1[1] * 2 >> 0x20));
      uVar4 = FUN_080001c8((int)((ulonglong)uVar1 * 0x19),(int)((ulonglong)uVar1 * 0x19 >> 0x20),
                           (int)((ulonglong)(uint)param_1[1] * 2),
                           (int)((ulonglong)(uint)param_1[1] * 2 >> 0x20));
      iVar5 = FUN_080001c8((int)((ulonglong)uVar1 * 0x19),(int)((ulonglong)uVar1 * 0x19 >> 0x20),
                           (int)((ulonglong)(uint)param_1[1] * 2),
                           (int)((ulonglong)(uint)param_1[1] * 2 >> 0x20));
      uVar1 = FUN_080001c8((int)((ulonglong)uVar1 * 0x19),(int)((ulonglong)uVar1 * 0x19 >> 0x20),
                           (int)((ulonglong)(uint)param_1[1] * 2),
                           (int)((ulonglong)(uint)param_1[1] * 2 >> 0x20));
      *(uint *)(*param_1 + 8) =
           (((iVar5 + (uVar1 / 100) * -100) * 8 + 0x32) / 100 & 7) +
           (uVar2 / 100) * 0x10 + (((iVar3 + (uVar4 / 100) * -100) * 8 + 0x32) / 100 & 0xf8) * 2;
      return;
    }
    uVar1 = FUN_08001e1c();
    uVar2 = FUN_080001c8((int)((ulonglong)uVar1 * 0x19),(int)((ulonglong)uVar1 * 0x19 >> 0x20),
                         (int)((ulonglong)(uint)param_1[1] * 2),
                         (int)((ulonglong)(uint)param_1[1] * 2 >> 0x20));
    iVar3 = FUN_080001c8((int)((ulonglong)uVar1 * 0x19),(int)((ulonglong)uVar1 * 0x19 >> 0x20),
                         (int)((ulonglong)(uint)param_1[1] * 2),
                         (int)((ulonglong)(uint)param_1[1] * 2 >> 0x20));
    uVar4 = FUN_080001c8((int)((ulonglong)uVar1 * 0x19),(int)((ulonglong)uVar1 * 0x19 >> 0x20),
                         (int)((ulonglong)(uint)param_1[1] * 2),
                         (int)((ulonglong)(uint)param_1[1] * 2 >> 0x20));
    iVar5 = FUN_080001c8((int)((ulonglong)uVar1 * 0x19),(int)((ulonglong)uVar1 * 0x19 >> 0x20),
                         (int)((ulonglong)(uint)param_1[1] * 2),
                         (int)((ulonglong)(uint)param_1[1] * 2 >> 0x20));
    uVar1 = FUN_080001c8((int)((ulonglong)uVar1 * 0x19),(int)((ulonglong)uVar1 * 0x19 >> 0x20),
                         (int)((ulonglong)(uint)param_1[1] * 2),
                         (int)((ulonglong)(uint)param_1[1] * 2 >> 0x20));
    *(uint *)(*param_1 + 8) =
         (((iVar5 + (uVar1 / 100) * -100) * 8 + 0x32) / 100 & 7) +
         (uVar2 / 100) * 0x10 + (((iVar3 + (uVar4 / 100) * -100) * 8 + 0x32) / 100 & 0xf8) * 2;
  }
  else {
    if ((*param_1 != DAT_08003344) && (*param_1 != DAT_08003348)) {
      uVar1 = FUN_08001dfc();
      iVar3 = FUN_080001c8((int)((ulonglong)uVar1 * 0x19),(int)((ulonglong)uVar1 * 0x19 >> 0x20),
                           (int)((ulonglong)(uint)param_1[1] * 4),
                           (int)((ulonglong)(uint)param_1[1] * 4 >> 0x20));
      uVar2 = FUN_080001c8((int)((ulonglong)uVar1 * 0x19),(int)((ulonglong)uVar1 * 0x19 >> 0x20),
                           (int)((ulonglong)(uint)param_1[1] * 4),
                           (int)((ulonglong)(uint)param_1[1] * 4 >> 0x20));
      uVar4 = FUN_080001c8((int)((ulonglong)uVar1 * 0x19),(int)((ulonglong)uVar1 * 0x19 >> 0x20),
                           (int)((ulonglong)(uint)param_1[1] * 4),
                           (int)((ulonglong)(uint)param_1[1] * 4 >> 0x20));
      iVar5 = FUN_080001c8((int)((ulonglong)uVar1 * 0x19),(int)((ulonglong)uVar1 * 0x19 >> 0x20),
                           (int)((ulonglong)(uint)param_1[1] * 4),
                           (int)((ulonglong)(uint)param_1[1] * 4 >> 0x20));
      uVar1 = FUN_080001c8((int)((ulonglong)uVar1 * 0x19),(int)((ulonglong)uVar1 * 0x19 >> 0x20),
                           (int)((ulonglong)(uint)param_1[1] * 4),
                           (int)((ulonglong)(uint)param_1[1] * 4 >> 0x20));
      *(uint *)(*param_1 + 8) =
           (((iVar5 + (uVar1 / 100) * -100) * 0x10 + 0x32) / 100 & 0xf) +
           (((iVar3 + (uVar2 / 100) * -100) * 0x10 + 0x32) / 100 & 0xf0) + (uVar4 / 100) * 0x10;
      return;
    }
    uVar1 = FUN_08001e1c();
    iVar3 = FUN_080001c8((int)((ulonglong)uVar1 * 0x19),(int)((ulonglong)uVar1 * 0x19 >> 0x20),
                         (int)((ulonglong)(uint)param_1[1] * 4),
                         (int)((ulonglong)(uint)param_1[1] * 4 >> 0x20));
    uVar2 = FUN_080001c8((int)((ulonglong)uVar1 * 0x19),(int)((ulonglong)uVar1 * 0x19 >> 0x20),
                         (int)((ulonglong)(uint)param_1[1] * 4),
                         (int)((ulonglong)(uint)param_1[1] * 4 >> 0x20));
    uVar4 = FUN_080001c8((int)((ulonglong)uVar1 * 0x19),(int)((ulonglong)uVar1 * 0x19 >> 0x20),
                         (int)((ulonglong)(uint)param_1[1] * 4),
                         (int)((ulonglong)(uint)param_1[1] * 4 >> 0x20));
    iVar5 = FUN_080001c8((int)((ulonglong)uVar1 * 0x19),(int)((ulonglong)uVar1 * 0x19 >> 0x20),
                         (int)((ulonglong)(uint)param_1[1] * 4),
                         (int)((ulonglong)(uint)param_1[1] * 4 >> 0x20));
    uVar1 = FUN_080001c8((int)((ulonglong)uVar1 * 0x19),(int)((ulonglong)uVar1 * 0x19 >> 0x20),
                         (int)((ulonglong)(uint)param_1[1] * 4),
                         (int)((ulonglong)(uint)param_1[1] * 4 >> 0x20));
    *(uint *)(*param_1 + 8) =
         (((iVar5 + (uVar1 / 100) * -100) * 0x10 + 0x32) / 100 & 0xf) +
         (((iVar3 + (uVar2 / 100) * -100) * 0x10 + 0x32) / 100 & 0xf0) + (uVar4 / 100) * 0x10;
  }
  return;
}


// ===== FUN_0800334c @ 0800334c

void FUN_0800334c(void)

{
  return;
}


// ===== FUN_08003350 @ 08003350

void FUN_08003350(void)

{
  int iVar1;
  int iVar2;
  
  if (*DAT_08003418 << 0x1a < 0) {
    iVar1 = DAT_08003418[1];
    iVar2 = *DAT_0800341c;
    *DAT_0800341c = *DAT_0800341c + 1;
    DAT_08003420[iVar2] = (char)iVar1;
    *DAT_08003418 = -0x21;
  }
  if (*DAT_0800341c == 4) {
    switch(*DAT_08003420) {
    case 0xa0:
    case 0xa1:
    case 0xa2:
    case 0xa3:
    case 0xa4:
      *DAT_08003424 = (uint)(byte)DAT_08003420[1] << 2;
      break;
    default:
      iVar1 = FUN_08000296(DAT_08003420,&DAT_08003428,4);
      if (iVar1 != 0) {
        *DAT_0800341c = 0;
        *DAT_08003430 = 1;
        *DAT_08003434 = 0xe1;
      }
    }
  }
  if ((*DAT_0800341c == 5) && (iVar1 = FUN_08000296(DAT_08003420,&DAT_08003428,4), iVar1 == 0)) {
    *DAT_08003434 = 0xb0;
    *DAT_08003430 = 2;
    *DAT_0800341c = 0;
  }
  if ((*DAT_0800341c == *DAT_08003424) && (*DAT_08003424 != 0)) {
    *DAT_08003430 = 1;
  }
  return;
}


// ===== FUN_08003438 @ 08003438

undefined4 FUN_08003438(int param_1,int param_2)

{
  undefined4 uVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  if (*(int *)(param_1 + 700) == 0) {
    uVar1 = 3;
  }
  else {
    iVar4 = *(int *)(param_1 + 700);
    if ((*(int *)(param_1 + param_2 * 0x14 + 0x18) == 0) ||
       (uVar3 = *(uint *)(param_1 + param_2 * 0x14 + 0x18),
       uVar2 = *(uint *)(*(int *)(param_1 + 0x2c4) + param_2 * 0x1c + 0x44),
       uVar3 != uVar2 * (uVar3 / uVar2))) {
      *(undefined4 *)(iVar4 + 0x214) = 0;
      (**(code **)(*(int *)(param_1 + 0x2c0) + 0x10))
                (*(undefined4 *)(iVar4 + 0x208),iVar4 + 0x210,param_2);
    }
    else {
      *(undefined4 *)(param_1 + param_2 * 0x14 + 0x18) = 0;
      FUN_080042ec(param_1,param_2,0);
    }
    uVar1 = 0;
  }
  return uVar1;
}


// ===== FUN_080036ba @ 080036ba

undefined4 FUN_080036ba(int param_1,int param_2)

{
  undefined4 uVar1;
  
  if (param_2 == 0) {
    uVar1 = 3;
  }
  else {
    *(int *)(param_1 + 0x2c0) = param_2;
    uVar1 = 0;
  }
  return uVar1;
}


// ===== FUN_080036d8 @ 080036d8

undefined4 FUN_080036d8(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = *(int *)(param_1 + 700);
  *(undefined4 *)(iVar1 + 0x208) = param_2;
  *(undefined4 *)(iVar1 + 0x210) = param_3;
  return 0;
}


// ===== FUN_080036ec @ 080036ec

undefined4 FUN_080036ec(int param_1,byte *param_2)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 local_20;
  undefined4 local_1c;
  
  iVar2 = *(int *)(param_1 + 700);
  local_1c = 0;
  local_20 = 0;
  uVar3 = 0;
  if ((*param_2 & 0x60) == 0) {
    bVar1 = param_2[1];
    if (bVar1 == 0) {
      if (*(char *)(param_1 + 0x29c) == '\x03') {
        FUN_08003906(param_1,&local_20,2);
      }
      else {
        FUN_080038ac(param_1,param_2);
        uVar3 = 3;
      }
    }
    else if (bVar1 != 1) {
      if (bVar1 == 10) {
        if (*(char *)(param_1 + 0x29c) == '\x03') {
          FUN_08003906(param_1,&local_1c,1);
        }
        else {
          FUN_080038ac(param_1,param_2);
          uVar3 = 3;
        }
      }
      else if (bVar1 == 0xb) {
        if (*(char *)(param_1 + 0x29c) != '\x03') {
          FUN_080038ac(param_1,param_2);
          uVar3 = 3;
        }
      }
      else {
        FUN_080038ac(param_1,param_2);
        uVar3 = 3;
      }
    }
  }
  else if ((*param_2 & 0x60) == 0x20) {
    if (*(short *)(param_2 + 6) == 0) {
      (**(code **)(*(int *)(param_1 + 0x2c0) + 8))(param_2[1],param_2,0);
    }
    else if ((*param_2 & 0x80) == 0) {
      *(byte *)(iVar2 + 0x200) = param_2[1];
      *(byte *)(iVar2 + 0x201) = param_2[6];
      FUN_080038c4(param_1,iVar2,*(undefined2 *)(param_2 + 6));
    }
    else {
      (**(code **)(*(int *)(param_1 + 0x2c0) + 8))(param_2[1],iVar2,*(undefined2 *)(param_2 + 6));
      FUN_08003906(param_1,iVar2,*(undefined2 *)(param_2 + 6));
    }
  }
  else {
    FUN_080038ac(param_1,param_2);
    uVar3 = 3;
  }
  return uVar3;
}


// ===== FUN_080037e6 @ 080037e6

undefined1 FUN_080037e6(int param_1)

{
  undefined1 uVar1;
  int iVar2;
  
  iVar2 = *(int *)(param_1 + 700);
  if (*(int *)(param_1 + 700) == 0) {
    uVar1 = 3;
  }
  else {
    uVar1 = *(int *)(iVar2 + 0x214) != 0;
    if (!(bool)uVar1) {
      *(undefined4 *)(iVar2 + 0x214) = 1;
      *(undefined4 *)(param_1 + 0x2c) = *(undefined4 *)(iVar2 + 0x210);
      FUN_080042ec(param_1,0x81,*(undefined4 *)(iVar2 + 0x208),*(undefined4 *)(iVar2 + 0x210));
    }
  }
  return uVar1;
}


// ===== FUN_08003822 @ 08003822

undefined4 FUN_08003822(int param_1,undefined4 param_2)

{
  if (*(int *)(param_1 + 0x2b8) != 0) {
    (**(code **)(*(int *)(param_1 + 0x2b8) + 4))(param_1,param_2);
  }
  return 0;
}


// ===== FUN_0800383e @ 0800383e

void FUN_0800383e(int param_1,int param_2)

{
  char cVar1;
  
  cVar1 = *(char *)(param_1 + 0x29c);
  if (((cVar1 == '\x01') || (cVar1 == '\x02')) || (cVar1 == '\x03')) {
    if (*(short *)(param_2 + 2) == 1) {
      *(undefined4 *)(param_1 + 0x2a4) = 0;
      FUN_08003928(param_1);
    }
  }
  else {
    FUN_080038ac(param_1,param_2);
  }
  return;
}


// ===== FUN_0800387c @ 0800387c

undefined4 FUN_0800387c(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  FUN_08004110(param_1,0,param_2,param_3);
  return 0;
}


// ===== FUN_08003894 @ 08003894

undefined4 FUN_08003894(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  FUN_080042ec(param_1,0,param_2,param_3);
  return 0;
}


// ===== FUN_080038ac @ 080038ac

void FUN_080038ac(undefined4 param_1)

{
  FUN_08004276(param_1,0x80);
  FUN_08004276(param_1,0);
  return;
}


// ===== FUN_080038c4 @ 080038c4

undefined4 FUN_080038c4(int param_1,undefined4 param_2,undefined4 param_3)

{
  *(undefined4 *)(param_1 + 0x294) = 3;
  *(undefined4 *)(param_1 + 0x158) = param_3;
  *(undefined4 *)(param_1 + 0x15c) = param_3;
  FUN_08004110(param_1,0,param_2,param_3);
  return 0;
}


// ===== FUN_080038ec @ 080038ec

undefined4 FUN_080038ec(int param_1)

{
  *(undefined4 *)(param_1 + 0x294) = 5;
  FUN_08004110(param_1,0,0);
  return 0;
}


// ===== FUN_08003906 @ 08003906

undefined4 FUN_08003906(int param_1,undefined4 param_2,undefined4 param_3)

{
  *(undefined4 *)(param_1 + 0x294) = 2;
  *(undefined4 *)(param_1 + 0x18) = param_3;
  *(undefined4 *)(param_1 + 0x1c) = param_3;
  FUN_080042ec(param_1,0,param_2,param_3);
  return 0;
}


// ===== FUN_08003928 @ 08003928

undefined4 FUN_08003928(int param_1)

{
  *(undefined4 *)(param_1 + 0x294) = 4;
  FUN_080042ec(param_1,0,0);
  return 0;
}


// ===== FUN_08003942 @ 08003942

int FUN_08003942(int param_1)

{
  int iVar1;
  
  *(undefined1 *)(param_1 + 0x29c) = 1;
  if (*(int *)(param_1 + 0x2b8) != 0) {
    (**(code **)(*(int *)(param_1 + 0x2b8) + 4))(param_1,*(undefined1 *)(param_1 + 4));
  }
  if (*(int *)(param_1 + 0x2cc) != 0) {
    *(undefined4 *)(param_1 + 0x2cc) = 0;
  }
  iVar1 = FUN_080042ba(param_1);
  if (iVar1 == 0) {
    iVar1 = FUN_08003fde(param_1);
  }
  return iVar1;
}


// ===== FUN_08003984 @ 08003984

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_08003984(int param_1,undefined4 param_2)

{
  if (param_1 == 0) {
    FUN_08003d56(s_CDC_Config_080039ab + 1,_DAT_080039a8,param_2);
  }
  else {
    FUN_08003d56(s_CDC_Config_080039ab + 1,_DAT_080039a8,param_2);
  }
  return _DAT_080039a8;
}


// ===== FUN_08003a94 @ 08003a94

void FUN_08003a94(int param_1,int param_2)

{
  char cVar1;
  
  if (*(short *)(param_2 + 6) == 1) {
    cVar1 = *(char *)(param_1 + 0x29c);
    if ((cVar1 == '\x01') || (cVar1 == '\x02')) {
      *(undefined4 *)(param_1 + 8) = 0;
      FUN_08003906(param_1,param_1 + 8,1);
    }
    else if (cVar1 == '\x03') {
      FUN_08003906(param_1,param_1 + 4,1);
    }
    else {
      FUN_080038ac(param_1,param_2);
    }
  }
  else {
    FUN_080038ac(param_1,param_2);
  }
  return;
}


// ===== FUN_08003aea @ 08003aea

void FUN_08003aea(int param_1,int param_2)

{
  bool bVar1;
  int iVar2;
  uint local_18;
  
  local_18 = 0;
  iVar2 = 0;
  bVar1 = false;
  switch((int)(uint)*(ushort *)(param_2 + 2) >> 8) {
  default:
    FUN_080038ac(param_1,param_2);
    bVar1 = true;
    break;
  case 1:
    iVar2 = (*(code *)**(undefined4 **)(param_1 + 0x2b4))(*(undefined1 *)(param_1 + 0x10),&local_18)
    ;
    break;
  case 2:
    if (*(char *)(param_1 + 0x10) == '\0') {
      iVar2 = (**(code **)(*(int *)(param_1 + 0x2b8) + 0x28))(&local_18);
      *(undefined1 *)(iVar2 + 1) = 2;
    }
    else {
      iVar2 = (**(code **)(*(int *)(param_1 + 0x2b8) + 0x2c))(&local_18);
      *(undefined1 *)(iVar2 + 1) = 2;
    }
    break;
  case 3:
    switch(*(undefined1 *)(param_2 + 2)) {
    case 0:
      bVar1 = *(int *)(*(int *)(param_1 + 0x2b4) + 4) == 0;
      if (bVar1) {
        FUN_080038ac(param_1,param_2);
      }
      else {
        iVar2 = (**(code **)(*(int *)(param_1 + 0x2b4) + 4))
                          (*(undefined1 *)(param_1 + 0x10),&local_18);
      }
      break;
    case 1:
      bVar1 = *(int *)(*(int *)(param_1 + 0x2b4) + 8) == 0;
      if (bVar1) {
        FUN_080038ac(param_1,param_2);
      }
      else {
        iVar2 = (**(code **)(*(int *)(param_1 + 0x2b4) + 8))
                          (*(undefined1 *)(param_1 + 0x10),&local_18);
      }
      break;
    case 2:
      bVar1 = *(int *)(*(int *)(param_1 + 0x2b4) + 0xc) == 0;
      if (bVar1) {
        FUN_080038ac(param_1,param_2);
      }
      else {
        iVar2 = (**(code **)(*(int *)(param_1 + 0x2b4) + 0xc))
                          (*(undefined1 *)(param_1 + 0x10),&local_18);
      }
      break;
    case 3:
      bVar1 = *(int *)(*(int *)(param_1 + 0x2b4) + 0x10) == 0;
      if (bVar1) {
        FUN_080038ac(param_1,param_2);
      }
      else {
        iVar2 = (**(code **)(*(int *)(param_1 + 0x2b4) + 0x10))
                          (*(undefined1 *)(param_1 + 0x10),&local_18);
      }
      break;
    case 4:
      bVar1 = *(int *)(*(int *)(param_1 + 0x2b4) + 0x14) == 0;
      if (bVar1) {
        FUN_080038ac(param_1,param_2);
      }
      else {
        iVar2 = (**(code **)(*(int *)(param_1 + 0x2b4) + 0x14))
                          (*(undefined1 *)(param_1 + 0x10),&local_18);
      }
      break;
    case 5:
      bVar1 = *(int *)(*(int *)(param_1 + 0x2b4) + 0x18) == 0;
      if (bVar1) {
        FUN_080038ac(param_1,param_2);
      }
      else {
        iVar2 = (**(code **)(*(int *)(param_1 + 0x2b4) + 0x18))
                          (*(undefined1 *)(param_1 + 0x10),&local_18);
      }
      break;
    default:
      FUN_080038ac(param_1,param_2);
      bVar1 = true;
    }
    break;
  case 6:
    bVar1 = *(char *)(param_1 + 0x10) != '\0';
    if (bVar1) {
      FUN_080038ac(param_1,param_2);
    }
    else {
      iVar2 = (**(code **)(*(int *)(param_1 + 0x2b8) + 0x34))(&local_18);
    }
    break;
  case 7:
    bVar1 = *(char *)(param_1 + 0x10) != '\0';
    if (bVar1) {
      FUN_080038ac(param_1,param_2);
    }
    else {
      iVar2 = (**(code **)(*(int *)(param_1 + 0x2b8) + 0x30))(&local_18);
      *(undefined1 *)(iVar2 + 1) = 7;
    }
  }
  if (!bVar1) {
    if (*(short *)(param_2 + 6) == 0) {
      FUN_08003928(param_1);
    }
    else if ((ushort)local_18 == 0) {
      FUN_080038ac(param_1,param_2);
    }
    else {
      if (*(ushort *)(param_2 + 6) <= (ushort)local_18) {
        local_18._0_2_ = *(ushort *)(param_2 + 6);
      }
      local_18 = (uint)(ushort)local_18;
      FUN_08003906(param_1,iVar2,local_18);
    }
  }
  return;
}


// ===== FUN_08003ce6 @ 08003ce6

char FUN_08003ce6(char *param_1)

{
  char cVar1;
  
  cVar1 = '\0';
  for (; *param_1 != '\0'; param_1 = param_1 + 1) {
    cVar1 = cVar1 + '\x01';
  }
  return cVar1;
}


// ===== FUN_08003cfc @ 08003cfc

void FUN_08003cfc(int param_1,int param_2)

{
  char cVar1;
  
  cVar1 = *(char *)(param_1 + 0x29c);
  if (((cVar1 == '\x01') || (cVar1 == '\x02')) || (cVar1 == '\x03')) {
    if (*(short *)(param_2 + 6) == 2) {
      *(undefined4 *)(param_1 + 0xc) = 1;
      if (*(int *)(param_1 + 0x2a4) != 0) {
        *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) | 2;
      }
      FUN_08003906(param_1,param_1 + 0xc,2);
    }
    else {
      FUN_080038ac(param_1,param_2);
    }
  }
  else {
    FUN_080038ac(param_1,param_2);
  }
  return;
}


// ===== FUN_08003d56 @ 08003d56

void FUN_08003d56(char *param_1,undefined1 *param_2,short *param_3)

{
  short sVar1;
  uint uVar2;
  
  if (param_1 != (char *)0x0) {
    sVar1 = FUN_08003ce6(param_1);
    *param_3 = sVar1 * 2 + 2;
    *param_2 = (char)*param_3;
    param_2[1] = 3;
    uVar2 = 2;
    for (; *param_1 != '\0'; param_1 = param_1 + 1) {
      param_2[uVar2] = *param_1;
      uVar2 = uVar2 + 1 & 0xff;
      param_2[uVar2] = 0;
      uVar2 = uVar2 + 1 & 0xff;
    }
  }
  return;
}


// ===== FUN_08003daa @ 08003daa

undefined4 FUN_08003daa(int param_1)

{
  undefined4 uVar1;
  
  if (param_1 == 0) {
    uVar1 = 0;
  }
  else if (param_1 == 1) {
    uVar1 = 3;
  }
  else if (param_1 == 2) {
    uVar1 = 1;
  }
  else if (param_1 == 3) {
    uVar1 = 3;
  }
  else {
    uVar1 = 3;
  }
  return uVar1;
}


// ===== FUN_08003dd6 @ 08003dd6

undefined4 FUN_08003dd6(undefined1 *param_1,int param_2,undefined1 param_3)

{
  undefined4 uVar1;
  
  if (param_1 == (undefined1 *)0x0) {
    uVar1 = 3;
  }
  else {
    if (*(int *)(param_1 + 0x2b8) != 0) {
      *(undefined4 *)(param_1 + 0x2b8) = 0;
    }
    if (*(int *)(param_1 + 0x2cc) != 0) {
      *(undefined4 *)(param_1 + 0x2cc) = 0;
    }
    if (param_2 != 0) {
      *(int *)(param_1 + 0x2b4) = param_2;
    }
    param_1[0x29c] = 1;
    *param_1 = param_3;
    uVar1 = FUN_08004034(param_1);
  }
  return uVar1;
}


// ===== FUN_08003e1a @ 08003e1a

undefined4 FUN_08003e1a(int param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_08001276(*(undefined4 *)(param_1 + 0x2c4),param_2);
  uVar1 = FUN_08003daa(uVar1);
  return uVar1;
}


// ===== FUN_08003e40 @ 08003e40

undefined4 FUN_08003e40(int param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_0800120c(*(undefined4 *)(param_1 + 0x2c4),param_2);
  uVar1 = FUN_08003daa(uVar1);
  return uVar1;
}


// ===== FUN_08003e66 @ 08003e66

int FUN_08003e66(int param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  
  if (param_2 == 0) {
    if (*(int *)(param_1 + 0x294) == 2) {
      if (*(uint *)(param_1 + 0x20) < *(uint *)(param_1 + 0x1c)) {
        *(int *)(param_1 + 0x1c) = *(int *)(param_1 + 0x1c) - *(int *)(param_1 + 0x20);
        FUN_08003894(param_1,param_3,*(undefined4 *)(param_1 + 0x1c));
        FUN_08004110(param_1,0,0);
      }
      else if (((*(int *)(param_1 + 0x20) == *(int *)(param_1 + 0x1c)) &&
               (*(uint *)(param_1 + 0x20) <= *(uint *)(param_1 + 0x18))) &&
              (*(uint *)(param_1 + 0x18) < *(uint *)(param_1 + 0x298))) {
        FUN_08003894(param_1,0);
        *(undefined4 *)(param_1 + 0x298) = 0;
        FUN_08004110(param_1,0,0);
      }
      else {
        if ((*(int *)(*(int *)(param_1 + 0x2b8) + 0xc) != 0) &&
           (*(char *)(param_1 + 0x29c) == '\x03')) {
          (**(code **)(*(int *)(param_1 + 0x2b8) + 0xc))(param_1);
        }
        FUN_08004276(param_1,0x80);
        FUN_080038ec(param_1);
      }
    }
    if (*(char *)(param_1 + 0x2a0) == '\x01') {
      FUN_08004378(param_1);
      *(undefined1 *)(param_1 + 0x2a0) = 0;
    }
  }
  else {
    if ((*(int *)(*(int *)(param_1 + 0x2b8) + 0x14) == 0) || (*(char *)(param_1 + 0x29c) != '\x03'))
    {
      return 3;
    }
    iVar1 = (**(code **)(*(int *)(param_1 + 0x2b8) + 0x14))(param_1,param_2);
    if (iVar1 != 0) {
      return iVar1;
    }
  }
  return 0;
}


// ===== FUN_08003f4c @ 08003f4c

int FUN_08003f4c(int param_1,int param_2,undefined4 param_3)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_2 == 0) {
    if (*(int *)(param_1 + 0x294) == 3) {
      if (*(uint *)(param_1 + 0x160) < *(uint *)(param_1 + 0x15c)) {
        *(int *)(param_1 + 0x15c) = *(int *)(param_1 + 0x15c) - *(int *)(param_1 + 0x160);
        if (*(uint *)(param_1 + 0x15c) < *(uint *)(param_1 + 0x160)) {
          uVar1 = *(undefined4 *)(param_1 + 0x15c);
        }
        else {
          uVar1 = *(undefined4 *)(param_1 + 0x160);
        }
        FUN_0800387c(param_1,param_3,uVar1);
      }
      else {
        if ((*(int *)(*(int *)(param_1 + 0x2b8) + 0x10) != 0) &&
           (*(char *)(param_1 + 0x29c) == '\x03')) {
          (**(code **)(*(int *)(param_1 + 0x2b8) + 0x10))(param_1);
        }
        FUN_08003928(param_1);
      }
    }
  }
  else {
    if ((*(int *)(*(int *)(param_1 + 0x2b8) + 0x18) == 0) || (*(char *)(param_1 + 0x29c) != '\x03'))
    {
      return 3;
    }
    iVar2 = (**(code **)(*(int *)(param_1 + 0x2b8) + 0x18))(param_1,param_2);
    if (iVar2 != 0) {
      return iVar2;
    }
  }
  return 0;
}


// ===== FUN_08003fde @ 08003fde

undefined4 FUN_08003fde(int param_1)

{
  undefined4 uVar1;
  
  uVar1 = FUN_080011d8(*(undefined4 *)(param_1 + 0x2c4));
  uVar1 = FUN_08003daa(uVar1);
  return uVar1;
}


// ===== FUN_08003ffc @ 08003ffc

longlong FUN_08003ffc(uint param_1)

{
  return (ulonglong)param_1 << 0x20;
}


// ===== FUN_08004002 @ 08004002

undefined4 FUN_08004002(int param_1)

{
  *(undefined1 *)(param_1 + 0x29c) = 1;
  if (*(int *)(param_1 + 0x2b8) != 0) {
    (**(code **)(*(int *)(param_1 + 0x2b8) + 4))(param_1,*(undefined1 *)(param_1 + 4));
  }
  return 0;
}


// ===== FUN_08004022 @ 08004022

void FUN_08004022(int param_1,undefined4 param_2)

{
  FUN_080012f2(*(undefined4 *)(param_1 + 0x2c4),param_2);
  return;
}


// ===== FUN_08004034 @ 08004034

undefined4 FUN_08004034(char *param_1)

{
  undefined4 *puVar1;
  int iVar2;
  
  puVar1 = DAT_08004098;
  if (*param_1 == '\0') {
    DAT_08004098[0x101] = param_1;
    *(undefined4 **)(param_1 + 0x2c4) = puVar1;
    puVar1 = DAT_08004098;
    *DAT_08004098 = 0x50000000;
    puVar1[1] = 4;
    puVar1 = DAT_08004098;
    DAT_08004098[3] = 2;
    puVar1[4] = 0;
    puVar1[6] = 2;
    puVar1[7] = 0;
    puVar1[8] = 0;
    puVar1[9] = 0;
    puVar1[0xb] = 0;
    puVar1[0xc] = 0;
    iVar2 = FUN_08001a50();
    if (iVar2 != 0) {
      FUN_080006a2();
    }
    FUN_08001132(DAT_08004098,0x80);
    FUN_0800113c(DAT_08004098,0,0x40);
    FUN_0800113c(DAT_08004098,1,0x80);
  }
  return 0;
}


// ===== FUN_0800409c @ 0800409c

undefined1 FUN_0800409c(int param_1,uint param_2)

{
  undefined1 uVar1;
  
  if ((param_2 & 0x80) == 0x80) {
    uVar1 = *(undefined1 *)(*(int *)(param_1 + 0x2c4) + (param_2 & 0x7f) * 0x1c + 0x3e);
  }
  else {
    uVar1 = *(undefined1 *)(*(int *)(param_1 + 0x2c4) + (param_2 & 0x7f) * 0x1c + 0x1fe);
  }
  return uVar1;
}


// ===== FUN_080040d4 @ 080040d4

undefined4 FUN_080040d4(void)

{
  return 0;
}


// ===== FUN_080040da @ 080040da

undefined4 FUN_080040da(void)

{
  return 0;
}


// ===== FUN_080040e0 @ 080040e0

undefined4 FUN_080040e0(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  uVar1 = FUN_08001308(*(undefined4 *)(param_1 + 0x2c4),param_2,param_4,param_3);
  uVar1 = FUN_08003daa(uVar1);
  return uVar1;
}


// ===== FUN_08004110 @ 08004110

undefined4 FUN_08004110(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  uVar1 = FUN_08001394(*(undefined4 *)(param_1 + 0x2c4),param_2,param_3,param_4);
  uVar1 = FUN_08003daa(uVar1);
  return uVar1;
}


// ===== FUN_08004140 @ 08004140

undefined4 FUN_08004140(int param_1)

{
  *(undefined1 *)(param_1 + 0x29c) = 1;
  *(undefined4 *)(param_1 + 0x294) = 0;
  *(undefined4 *)(param_1 + 4) = 0;
  *(undefined4 *)(param_1 + 0x2a4) = 0;
  if (*(int *)(param_1 + 700) != 0) {
    (**(code **)(*(int *)(param_1 + 0x2b8) + 4))(param_1,*(undefined1 *)(param_1 + 4));
  }
  FUN_080040e0(param_1,0,0,0x40);
  *(undefined2 *)(param_1 + 0x164) = 1;
  *(undefined4 *)(param_1 + 0x160) = 0x40;
  FUN_080040e0(param_1,0x80,0,0x40);
  *(undefined2 *)(param_1 + 0x24) = 1;
  *(undefined4 *)(param_1 + 0x20) = 0x40;
  return 0;
}


// ===== FUN_0800419a @ 0800419a

undefined4 FUN_0800419a(int param_1)

{
  if (*(char *)(param_1 + 0x29c) == '\x04') {
    *(undefined1 *)(param_1 + 0x29c) = *(undefined1 *)(param_1 + 0x29d);
  }
  return 0;
}


// ===== FUN_080041b0 @ 080041b0

undefined4 FUN_080041b0(int param_1)

{
  if ((*(char *)(param_1 + 0x29c) == '\x03') && (*(int *)(*(int *)(param_1 + 0x2b8) + 0x1c) != 0)) {
    (**(code **)(*(int *)(param_1 + 0x2b8) + 0x1c))(param_1);
  }
  return 0;
}


// ===== FUN_080041d2 @ 080041d2

undefined4 FUN_080041d2(int param_1,undefined1 param_2)

{
  *(undefined1 *)(param_1 + 0x10) = param_2;
  return 0;
}


// ===== FUN_080041da @ 080041da

undefined4 FUN_080041da(int param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_08001ce0(*(undefined4 *)(param_1 + 0x2c4),param_2);
  uVar1 = FUN_08003daa(uVar1);
  return uVar1;
}


// ===== FUN_08004200 @ 08004200

undefined4 FUN_08004200(int param_1,undefined4 param_2)

{
  byte bVar1;
  undefined4 uVar2;
  
  FUN_0800431c(param_1 + 0x2aa,param_2);
  *(undefined4 *)(param_1 + 0x294) = 1;
  *(uint *)(param_1 + 0x298) = (uint)*(ushort *)(param_1 + 0x2b0);
  bVar1 = *(byte *)(param_1 + 0x2aa) & 0x1f;
  if ((*(byte *)(param_1 + 0x2aa) & 0x1f) == 0) {
    uVar2 = FUN_08004518(param_1,param_1 + 0x2aa);
  }
  else if (bVar1 == 1) {
    uVar2 = FUN_080047e8(param_1,param_1 + 0x2aa);
  }
  else if (bVar1 == 2) {
    uVar2 = FUN_080045be(param_1,param_1 + 0x2aa);
  }
  else {
    uVar2 = FUN_08004276(param_1,*(byte *)(param_1 + 0x2aa) & 0x80);
  }
  return uVar2;
}


// ===== FUN_08004276 @ 08004276

undefined4 FUN_08004276(int param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_080013ec(*(undefined4 *)(param_1 + 0x2c4),param_2);
  uVar1 = FUN_08003daa(uVar1);
  return uVar1;
}


// ===== FUN_0800429c @ 0800429c

undefined4 FUN_0800429c(int param_1)

{
  undefined4 uVar1;
  
  uVar1 = FUN_08001d28(*(undefined4 *)(param_1 + 0x2c4));
  uVar1 = FUN_08003daa(uVar1);
  return uVar1;
}


// ===== FUN_080042ba @ 080042ba

undefined4 FUN_080042ba(int param_1)

{
  undefined4 uVar1;
  
  uVar1 = FUN_08001d72(*(undefined4 *)(param_1 + 0x2c4));
  uVar1 = FUN_08003daa(uVar1);
  return uVar1;
}


// ===== FUN_080042d8 @ 080042d8

undefined4 FUN_080042d8(int param_1)

{
  *(undefined1 *)(param_1 + 0x29d) = *(undefined1 *)(param_1 + 0x29c);
  *(undefined1 *)(param_1 + 0x29c) = 4;
  return 0;
}


// ===== FUN_080042ec @ 080042ec

undefined4 FUN_080042ec(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  uVar1 = FUN_08001476(*(undefined4 *)(param_1 + 0x2c4),param_2,param_3,param_4);
  uVar1 = FUN_08003daa(uVar1);
  return uVar1;
}


// ===== FUN_0800431c @ 0800431c

void FUN_0800431c(undefined1 *param_1,undefined1 *param_2)

{
  undefined2 uVar1;
  
  *param_1 = *param_2;
  param_1[1] = param_2[1];
  uVar1 = FUN_08002dda(param_2 + 2);
  *(undefined2 *)(param_1 + 2) = uVar1;
  uVar1 = FUN_08002dda(param_2 + 4);
  *(undefined2 *)(param_1 + 4) = uVar1;
  uVar1 = FUN_08002dda(param_2 + 6);
  *(undefined2 *)(param_1 + 6) = uVar1;
  return;
}


// ===== FUN_08004352 @ 08004352

undefined4 FUN_08004352(int param_1,int param_2)

{
  undefined4 uVar1;
  undefined4 local_10;
  
  local_10 = 0;
  if (param_2 == 0) {
    uVar1 = 3;
  }
  else {
    *(int *)(param_1 + 0x2b8) = param_2;
    uVar1 = (**(code **)(*(int *)(param_1 + 0x2b8) + 0x28))(&local_10);
    *(undefined4 *)(param_1 + 0x2cc) = uVar1;
    uVar1 = 0;
  }
  return uVar1;
}


// ===== FUN_08004378 @ 08004378

longlong FUN_08004378(uint param_1)

{
  return (ulonglong)param_1 << 0x20;
}


// ===== FUN_0800437e @ 0800437e

void FUN_0800437e(int param_1,int param_2)

{
  byte bVar1;
  byte bVar2;
  
  if (((*(short *)(param_2 + 4) == 0) && (*(short *)(param_2 + 6) == 0)) &&
     (*(ushort *)(param_2 + 2) < 0x80)) {
    bVar1 = *(byte *)(param_2 + 2);
    bVar2 = bVar1 & 0x7f;
    if (*(char *)(param_1 + 0x29c) == '\x03') {
      FUN_080038ac(param_1,param_2);
    }
    else {
      *(byte *)(param_1 + 0x29e) = bVar2;
      FUN_080041da(param_1,bVar2);
      FUN_08003928(param_1);
      if ((bVar1 & 0x7f) == 0) {
        *(undefined1 *)(param_1 + 0x29c) = 1;
      }
      else {
        *(undefined1 *)(param_1 + 0x29c) = 2;
      }
    }
  }
  else {
    FUN_080038ac(param_1,param_2);
  }
  return;
}


// ===== FUN_080043d8 @ 080043d8

undefined4 FUN_080043d8(int param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = 3;
  if (*(int *)(param_1 + 0x2b8) != 0) {
    uVar1 = (*(code *)**(undefined4 **)(param_1 + 0x2b8))(param_1,param_2);
  }
  return uVar1;
}


// ===== FUN_080043f8 @ 080043f8

int FUN_080043f8(int param_1,int param_2)

{
  byte *pbVar1;
  int iVar2;
  
  pbVar1 = DAT_080044f0;
  iVar2 = 0;
  *DAT_080044f0 = *(byte *)(param_2 + 2);
  if (*pbVar1 < 2) {
    if (*(char *)(param_1 + 0x29c) == '\x02') {
      if (*DAT_080044f0 == 0) {
        FUN_08003928(param_1);
      }
      else {
        *(uint *)(param_1 + 4) = (uint)*DAT_080044f0;
        iVar2 = FUN_080043d8(param_1,*DAT_080044f0);
        if (iVar2 == 0) {
          FUN_08003928(param_1);
          *(undefined1 *)(param_1 + 0x29c) = 3;
        }
        else {
          FUN_080038ac(param_1,param_2);
        }
      }
    }
    else if (*(char *)(param_1 + 0x29c) == '\x03') {
      if (*DAT_080044f0 == 0) {
        *(undefined1 *)(param_1 + 0x29c) = 2;
        *(uint *)(param_1 + 4) = (uint)*DAT_080044f0;
        FUN_08003822(param_1,*DAT_080044f0);
        FUN_08003928(param_1);
      }
      else if (*(uint *)(param_1 + 4) == (uint)*DAT_080044f0) {
        FUN_08003928(param_1);
      }
      else {
        FUN_08003822(param_1,*(undefined1 *)(param_1 + 4));
        *(uint *)(param_1 + 4) = (uint)*DAT_080044f0;
        iVar2 = FUN_080043d8(param_1,*DAT_080044f0);
        if (iVar2 == 0) {
          FUN_08003928(param_1);
        }
        else {
          FUN_080038ac(param_1,param_2);
          FUN_08003822(param_1,*(undefined1 *)(param_1 + 4));
          *(undefined1 *)(param_1 + 0x29c) = 2;
        }
      }
    }
    else {
      FUN_080038ac(param_1,param_2);
      FUN_08003822(param_1,*DAT_080044f0);
      iVar2 = 3;
    }
  }
  else {
    FUN_080038ac(param_1,param_2);
    iVar2 = 3;
  }
  return iVar2;
}


// ===== FUN_080044f4 @ 080044f4

void FUN_080044f4(int param_1,int param_2)

{
  if (*(short *)(param_2 + 2) == 1) {
    *(undefined4 *)(param_1 + 0x2a4) = 1;
    FUN_08003928(param_1);
  }
  return;
}


// ===== FUN_0800450c @ 0800450c

void FUN_0800450c(undefined4 param_1)

{
  FUN_0800429c(param_1);
  return;
}


// ===== FUN_08004518 @ 08004518

undefined4 FUN_08004518(int param_1,byte *param_2)

{
  byte bVar1;
  undefined4 uVar2;
  
  uVar2 = 0;
  bVar1 = *param_2 & 0x60;
  if ((*param_2 & 0x60) == 0) {
    switch(param_2[1]) {
    case 0:
      FUN_08003cfc(param_1,param_2);
      break;
    case 1:
      FUN_0800383e(param_1,param_2);
      break;
    default:
      FUN_080038ac(param_1,param_2);
      break;
    case 3:
      FUN_080044f4(param_1,param_2);
      break;
    case 5:
      FUN_0800437e(param_1,param_2);
      break;
    case 6:
      FUN_08003aea(param_1,param_2);
      break;
    case 8:
      FUN_08003a94(param_1,param_2);
      break;
    case 9:
      uVar2 = FUN_080043f8(param_1,param_2);
    }
  }
  else if ((bVar1 == 0x20) || (bVar1 == 0x40)) {
    uVar2 = (**(code **)(*(int *)(param_1 + 0x2b8) + 8))(param_1,param_2);
  }
  else {
    FUN_080038ac(param_1,param_2);
  }
  return uVar2;
}


// ===== FUN_080045be @ 080045be

undefined4 FUN_080045be(int param_1,byte *param_2)

{
  byte bVar1;
  undefined4 *puVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  
  uVar5 = 0;
  uVar4 = (uint)param_2[4];
  bVar1 = *param_2 & 0x60;
  if ((*param_2 & 0x60) == 0) {
    bVar1 = param_2[1];
    if (bVar1 == 0) {
      if (*(char *)(param_1 + 0x29c) == '\x02') {
        if ((uVar4 == 0) || (uVar4 == 0x80)) {
          if ((uVar4 & 0x80) == 0x80) {
            puVar2 = (undefined4 *)(param_1 + 0x14 + (uVar4 & 0x7f) * 0x14);
          }
          else {
            puVar2 = (undefined4 *)(param_1 + 0x154 + (uVar4 & 0x7f) * 0x14);
          }
          *puVar2 = 0;
          FUN_08003906(param_1,puVar2,2);
        }
        else {
          FUN_080038ac(param_1,param_2);
        }
      }
      else if (*(char *)(param_1 + 0x29c) == '\x03') {
        if ((uVar4 & 0x80) == 0x80) {
          if (*(short *)(param_1 + (uVar4 & 0xf) * 0x14 + 0x24) == 0) {
            FUN_080038ac(param_1,param_2);
            return 0;
          }
        }
        else if (*(short *)(param_1 + (uVar4 & 0xf) * 0x14 + 0x164) == 0) {
          FUN_080038ac(param_1,param_2);
          return 0;
        }
        if ((uVar4 & 0x80) == 0x80) {
          puVar2 = (undefined4 *)(param_1 + 0x14 + (uVar4 & 0x7f) * 0x14);
        }
        else {
          puVar2 = (undefined4 *)(param_1 + 0x154 + (uVar4 & 0x7f) * 0x14);
        }
        if ((uVar4 == 0) || (uVar4 == 0x80)) {
          *puVar2 = 0;
        }
        else {
          iVar3 = FUN_0800409c(param_1,uVar4);
          if (iVar3 == 0) {
            *puVar2 = 0;
          }
          else {
            *puVar2 = 1;
          }
        }
        FUN_08003906(param_1,puVar2,2);
      }
      else {
        FUN_080038ac(param_1,param_2);
      }
    }
    else if (bVar1 == 1) {
      if (*(char *)(param_1 + 0x29c) == '\x02') {
        if ((uVar4 == 0) || (uVar4 == 0x80)) {
          FUN_080038ac(param_1,param_2);
        }
        else {
          FUN_08004276(param_1,uVar4);
          FUN_08004276(param_1,0x80);
        }
      }
      else if (*(char *)(param_1 + 0x29c) == '\x03') {
        if (*(short *)(param_2 + 2) == 0) {
          if ((param_2[4] & 0x7f) != 0) {
            FUN_08003e1a(param_1,uVar4);
          }
          FUN_08003928(param_1);
          (**(code **)(*(int *)(param_1 + 0x2b8) + 8))(param_1,param_2);
        }
      }
      else {
        FUN_080038ac(param_1,param_2);
      }
    }
    else if (bVar1 == 3) {
      if (*(char *)(param_1 + 0x29c) == '\x02') {
        if ((uVar4 == 0) || (uVar4 == 0x80)) {
          FUN_080038ac(param_1,param_2);
        }
        else {
          FUN_08004276(param_1,uVar4);
          FUN_08004276(param_1,0x80);
        }
      }
      else if (*(char *)(param_1 + 0x29c) == '\x03') {
        if ((((*(short *)(param_2 + 2) == 0) && (uVar4 != 0)) && (uVar4 != 0x80)) &&
           (*(short *)(param_2 + 6) == 0)) {
          FUN_08004276(param_1,uVar4);
        }
        FUN_08003928(param_1);
      }
      else {
        FUN_080038ac(param_1,param_2);
      }
    }
    else {
      FUN_080038ac(param_1,param_2);
    }
  }
  else if ((bVar1 == 0x20) || (bVar1 == 0x40)) {
    uVar5 = (**(code **)(*(int *)(param_1 + 0x2b8) + 8))(param_1,param_2);
  }
  else {
    FUN_080038ac(param_1,param_2);
  }
  return uVar5;
}


// ===== FUN_080047e8 @ 080047e8

int FUN_080047e8(int param_1,byte *param_2)

{
  char cVar1;
  byte bVar2;
  int iVar3;
  
  iVar3 = 0;
  bVar2 = *param_2 & 0x60;
  if ((((*param_2 & 0x60) == 0) || (bVar2 == 0x20)) || (bVar2 == 0x40)) {
    cVar1 = *(char *)(param_1 + 0x29c);
    if (((cVar1 == '\x01') || (cVar1 == '\x02')) || (cVar1 == '\x03')) {
      if (param_2[4] < 2) {
        iVar3 = (**(code **)(*(int *)(param_1 + 0x2b8) + 8))(param_1,param_2);
        if ((*(short *)(param_2 + 6) == 0) && (iVar3 == 0)) {
          FUN_08003928(param_1);
        }
      }
      else {
        FUN_080038ac(param_1,param_2);
      }
    }
    else {
      FUN_080038ac(param_1,param_2);
    }
  }
  else {
    FUN_080038ac(param_1,param_2);
  }
  return iVar3;
}


// ===== FUN_08004868 @ 08004868

undefined4 FUN_08004868(int param_1,byte *param_2)

{
  uint uVar1;
  
  uVar1 = (uint)*param_2;
  if (param_2[1] == 1) {
    *(uint *)(param_1 + 0x81c) = *(uint *)(param_1 + 0x81c) | 1 << (*param_2 & 0xf) & 0xffffU;
    if ((*(uint *)(param_1 + 0x900 + uVar1 * 0x20) & 0x8000) == 0) {
      *(uint *)(param_1 + 0x900 + uVar1 * 0x20) =
           *(ushort *)(param_2 + 8) & 0x7ff | (uint)param_2[3] << 0x12 | uVar1 << 0x16 | 0x10008000
           | *(uint *)(param_1 + 0x900 + uVar1 * 0x20);
    }
  }
  else {
    *(uint *)(param_1 + 0x81c) =
         *(uint *)(param_1 + 0x81c) | DAT_08004934 & (1 << (*param_2 & 0xf)) << 0x10;
    if ((*(uint *)(param_1 + 0xb00 + uVar1 * 0x20) & 0x8000) == 0) {
      *(uint *)(param_1 + 0xb00 + uVar1 * 0x20) =
           *(ushort *)(param_2 + 8) & 0x7ff | (uint)param_2[3] << 0x12 | 0x10008000 |
           *(uint *)(param_1 + 0xb00 + uVar1 * 0x20);
    }
  }
  return 0;
}


// ===== FUN_08004938 @ 08004938

undefined4 FUN_08004938(int param_1)

{
  *(uint *)(param_1 + 0x900) = *(uint *)(param_1 + 0x900) & 0xfffff800;
  *(uint *)(param_1 + 0x804) = *(uint *)(param_1 + 0x804) | 0x100;
  return 0;
}


// ===== FUN_08004960 @ 08004960

undefined4 FUN_08004960(int param_1)

{
  undefined4 uVar1;
  int in_stack_00000000;
  int in_stack_00000008;
  int in_stack_00000018;
  int in_stack_00000024;
  
  if (in_stack_00000008 == 1) {
    *(uint *)(param_1 + 0x38) = *(uint *)(param_1 + 0x38) & 0xfffeffff;
    *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) & DAT_080049e0;
    *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) & 0xffcfffff;
    if (in_stack_00000024 == 1) {
      *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) | 0x100000;
    }
    uVar1 = FUN_080049e4(param_1);
  }
  else {
    *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) | 0x40;
    uVar1 = FUN_080049e4(param_1);
    if (in_stack_00000018 == 0) {
      *(uint *)(param_1 + 0x38) = *(uint *)(param_1 + 0x38) | 0x10000;
    }
    else {
      *(uint *)(param_1 + 0x38) = *(uint *)(param_1 + 0x38) & 0xfffeffff;
    }
  }
  if (in_stack_00000000 == 1) {
    *(uint *)(param_1 + 8) = *(uint *)(param_1 + 8) | 6;
    *(uint *)(param_1 + 8) = *(uint *)(param_1 + 8) | 0x20;
  }
  return uVar1;
}


// ===== FUN_080049e4 @ 080049e4

undefined4 FUN_080049e4(int param_1)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    uVar1 = uVar1 + 1;
    if (DAT_08004a2c < uVar1) {
      return 3;
    }
  } while ((*(uint *)(param_1 + 0x10) & 0x80000000) == 0);
  uVar1 = 0;
  *(uint *)(param_1 + 0x10) = *(uint *)(param_1 + 0x10) | 1;
  do {
    uVar1 = uVar1 + 1;
    if (DAT_08004a2c < uVar1) {
      return 3;
    }
  } while ((*(uint *)(param_1 + 0x10) & 1) != 0);
  return 0;
}


// ===== FUN_08004a30 @ 08004a30

undefined4 FUN_08004a30(int param_1,byte *param_2)

{
  uint uVar1;
  
  uVar1 = (uint)*param_2;
  if (param_2[1] == 1) {
    if ((*(uint *)(param_1 + 0x900 + uVar1 * 0x20) & 0x80000000) == 0x80000000) {
      *(uint *)(param_1 + 0x900 + uVar1 * 0x20) =
           *(uint *)(param_1 + 0x900 + uVar1 * 0x20) | 0x8000000;
      *(uint *)(param_1 + 0x900 + uVar1 * 0x20) =
           *(uint *)(param_1 + 0x900 + uVar1 * 0x20) | 0x40000000;
    }
    *(uint *)(param_1 + 0x83c) = *(uint *)(param_1 + 0x83c) & ~(1 << (*param_2 & 0xf) & 0xffffU);
    *(uint *)(param_1 + 0x81c) = *(uint *)(param_1 + 0x81c) & ~(1 << (*param_2 & 0xf) & 0xffffU);
    *(uint *)(param_1 + 0x900 + uVar1 * 0x20) =
         *(uint *)(param_1 + 0x900 + uVar1 * 0x20) & DAT_08004b70;
  }
  else {
    if ((*(uint *)(param_1 + 0xb00 + uVar1 * 0x20) & 0x80000000) == 0x80000000) {
      *(uint *)(param_1 + 0xb00 + uVar1 * 0x20) =
           *(uint *)(param_1 + 0xb00 + uVar1 * 0x20) | 0x8000000;
      *(uint *)(param_1 + 0xb00 + uVar1 * 0x20) =
           *(uint *)(param_1 + 0xb00 + uVar1 * 0x20) | 0x40000000;
    }
    *(uint *)(param_1 + 0x83c) =
         *(uint *)(param_1 + 0x83c) & ~(DAT_08004b74 & (1 << (*param_2 & 0xf)) << 0x10);
    *(uint *)(param_1 + 0x81c) =
         *(uint *)(param_1 + 0x81c) & ~(DAT_08004b74 & (1 << (*param_2 & 0xf)) << 0x10);
    *(uint *)(param_1 + 0xb00 + uVar1 * 0x20) =
         *(uint *)(param_1 + 0xb00 + uVar1 * 0x20) & DAT_08004b78;
  }
  return 0;
}


// ===== FUN_08004b7c @ 08004b7c

undefined4 FUN_08004b7c(int param_1)

{
  *(uint *)(param_1 + 0x804) = *(uint *)(param_1 + 0x804) & 0xfffffffd;
  FUN_08000a30(3);
  return 0;
}


// ===== FUN_08004b9c @ 08004b9c

undefined4 FUN_08004b9c(int param_1)

{
  *(uint *)(param_1 + 0x804) = *(uint *)(param_1 + 0x804) | 2;
  FUN_08000a30(3);
  return 0;
}


// ===== FUN_08004bbc @ 08004bbc

bool FUN_08004bbc(int param_1,uint param_2,undefined4 param_3,int param_4,int param_5,
                 undefined4 param_6,int param_7,int param_8)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int in_stack_0000001c;
  
  for (uVar3 = 0; uVar3 < 0xf; uVar3 = uVar3 + 1) {
    *(undefined4 *)(param_1 + 0x104 + uVar3 * 4) = 0;
  }
  if (in_stack_0000001c == 0) {
    *(uint *)(param_1 + 0x804) = *(uint *)(param_1 + 0x804) | 2;
    *(uint *)(param_1 + 0x38) = *(uint *)(param_1 + 0x38) | 0x200000;
    *(uint *)(param_1 + 0x38) = *(uint *)(param_1 + 0x38) & 0xfff7ffff;
    *(uint *)(param_1 + 0x38) = *(uint *)(param_1 + 0x38) & 0xfffbffff;
  }
  else {
    *(uint *)(param_1 + 0x38) = *(uint *)(param_1 + 0x38) & 0xffdfffff;
    *(uint *)(param_1 + 0x38) = *(uint *)(param_1 + 0x38) | 0x80000;
  }
  *(undefined4 *)(param_1 + 0xe00) = 0;
  *(undefined4 *)(param_1 + 0x800) = *(undefined4 *)(param_1 + 0x800);
  if (param_7 == 1) {
    if (param_4 == 0) {
      FUN_080056d0(param_1,0);
    }
    else {
      FUN_080056d0(param_1,1);
    }
  }
  else {
    FUN_080056d0(param_1,3);
  }
  iVar1 = FUN_0800549c(param_1,0x10);
  iVar2 = FUN_08005470(param_1);
  *(undefined4 *)(param_1 + 0x810) = 0;
  *(undefined4 *)(param_1 + 0x814) = 0;
  *(undefined4 *)(param_1 + 0x81c) = 0;
  for (uVar3 = 0; uVar3 < param_2; uVar3 = uVar3 + 1) {
    if ((*(uint *)(param_1 + 0x900 + uVar3 * 0x20) & 0x80000000) == 0x80000000) {
      if (uVar3 == 0) {
        *(undefined4 *)(param_1 + 0x900) = 0x8000000;
      }
      else {
        *(undefined4 *)(param_1 + 0x900 + uVar3 * 0x20) = 0x48000000;
      }
    }
    else {
      *(undefined4 *)(param_1 + 0x900 + uVar3 * 0x20) = 0;
    }
    *(undefined4 *)(param_1 + uVar3 * 0x20 + 0x910) = 0;
    *(undefined4 *)(param_1 + uVar3 * 0x20 + 0x908) = 0xfb7f;
  }
  for (uVar3 = 0; uVar3 < param_2; uVar3 = uVar3 + 1) {
    if ((*(uint *)(param_1 + 0xb00 + uVar3 * 0x20) & 0x80000000) == 0x80000000) {
      if (uVar3 == 0) {
        *(undefined4 *)(param_1 + 0xb00) = 0x8000000;
      }
      else {
        *(undefined4 *)(param_1 + 0xb00 + uVar3 * 0x20) = 0x48000000;
      }
    }
    else {
      *(undefined4 *)(param_1 + 0xb00 + uVar3 * 0x20) = 0;
    }
    *(undefined4 *)(param_1 + uVar3 * 0x20 + 0xb10) = 0;
    *(undefined4 *)(param_1 + uVar3 * 0x20 + 0xb08) = 0xfb7f;
  }
  *(uint *)(param_1 + 0x810) = *(uint *)(param_1 + 0x810) & 0xfffffeff;
  *(undefined4 *)(param_1 + 0x18) = 0;
  *(undefined4 *)(param_1 + 0x14) = 0xbfffffff;
  if (param_5 == 0) {
    *(uint *)(param_1 + 0x18) = *(uint *)(param_1 + 0x18) | 0x10;
  }
  *(uint *)(param_1 + 0x18) = *(uint *)(param_1 + 0x18) | DAT_08004d94;
  if (param_8 != 0) {
    *(uint *)(param_1 + 0x18) = *(uint *)(param_1 + 0x18) | 8;
  }
  if (in_stack_0000001c == 1) {
    *(uint *)(param_1 + 0x18) = *(uint *)(param_1 + 0x18) | DAT_08004d98;
  }
  return iVar2 != 0 || iVar1 != 0;
}


// ===== FUN_08004d9c @ 08004d9c

undefined4 FUN_08004d9c(int param_1)

{
  *(uint *)(param_1 + 8) = *(uint *)(param_1 + 8) & 0xfffffffe;
  return 0;
}


// ===== FUN_08004dac @ 08004dac

undefined4 FUN_08004dac(int param_1,byte *param_2,int param_3)

{
  uint uVar1;
  
  uVar1 = (uint)*param_2;
  if (param_2[1] == 1) {
    if (*(int *)(param_2 + 0x14) == 0) {
      *(uint *)(param_1 + uVar1 * 0x20 + 0x910) =
           *(uint *)(param_1 + uVar1 * 0x20 + 0x910) & DAT_08004f80;
      *(uint *)(param_1 + uVar1 * 0x20 + 0x910) =
           *(uint *)(param_1 + uVar1 * 0x20 + 0x910) | 0x80000;
      *(uint *)(param_1 + uVar1 * 0x20 + 0x910) =
           *(uint *)(param_1 + uVar1 * 0x20 + 0x910) & 0xfff80000;
    }
    else {
      *(uint *)(param_1 + uVar1 * 0x20 + 0x910) =
           *(uint *)(param_1 + uVar1 * 0x20 + 0x910) & 0xfff80000;
      *(uint *)(param_1 + uVar1 * 0x20 + 0x910) =
           *(uint *)(param_1 + uVar1 * 0x20 + 0x910) & DAT_08004f80;
      if (*(uint *)(param_2 + 8) < *(uint *)(param_2 + 0x14)) {
        *(undefined4 *)(param_2 + 0x14) = *(undefined4 *)(param_2 + 8);
      }
      *(uint *)(param_1 + uVar1 * 0x20 + 0x910) =
           *(uint *)(param_1 + uVar1 * 0x20 + 0x910) | 0x80000;
      *(uint *)(param_1 + uVar1 * 0x20 + 0x910) =
           *(uint *)(param_1 + uVar1 * 0x20 + 0x910) | *(uint *)(param_2 + 0x14) & 0x7ffff;
    }
    if (param_3 == 1) {
      if (*(int *)(param_2 + 0x10) != 0) {
        *(undefined4 *)(param_1 + uVar1 * 0x20 + 0x914) = *(undefined4 *)(param_2 + 0x10);
      }
      *(uint *)(param_1 + 0x900 + uVar1 * 0x20) =
           *(uint *)(param_1 + 0x900 + uVar1 * 0x20) | 0x84000000;
    }
    else {
      *(uint *)(param_1 + 0x900 + uVar1 * 0x20) =
           *(uint *)(param_1 + 0x900 + uVar1 * 0x20) | 0x84000000;
      if (*(int *)(param_2 + 0x14) != 0) {
        *(uint *)(param_1 + 0x834) = *(uint *)(param_1 + 0x834) | 1 << (*param_2 & 0xf);
      }
    }
  }
  else {
    *(uint *)(param_1 + uVar1 * 0x20 + 0xb10) =
         *(uint *)(param_1 + uVar1 * 0x20 + 0xb10) & 0xfff80000;
    *(uint *)(param_1 + uVar1 * 0x20 + 0xb10) =
         *(uint *)(param_1 + uVar1 * 0x20 + 0xb10) & DAT_08004f80;
    if (*(int *)(param_2 + 0x14) != 0) {
      *(undefined4 *)(param_2 + 0x14) = *(undefined4 *)(param_2 + 8);
    }
    *(uint *)(param_1 + uVar1 * 0x20 + 0xb10) = *(uint *)(param_1 + uVar1 * 0x20 + 0xb10) | 0x80000;
    *(uint *)(param_1 + uVar1 * 0x20 + 0xb10) =
         *(uint *)(param_1 + uVar1 * 0x20 + 0xb10) | *(uint *)(param_2 + 8) & 0x7ffff;
    if ((param_3 == 1) && (*(int *)(param_2 + 0xc) != 0)) {
      *(undefined4 *)(param_1 + uVar1 * 0x20 + 0xb14) = *(undefined4 *)(param_2 + 0xc);
    }
    *(uint *)(param_1 + 0xb00 + uVar1 * 0x20) =
         *(uint *)(param_1 + 0xb00 + uVar1 * 0x20) | 0x84000000;
  }
  return 0;
}


// ===== FUN_08004f84 @ 08004f84

undefined4 FUN_08004f84(int param_1,int param_2,undefined4 param_3)

{
  if ((*(uint *)(param_1 + 0x40) <= DAT_08004ff0) ||
     ((*(uint *)(param_1 + 0xb00) & 0x80000000) != 0x80000000)) {
    *(undefined4 *)(param_1 + 0xb10) = 0;
    *(uint *)(param_1 + 0xb10) = *(uint *)(param_1 + 0xb10) | 0x80000;
    *(uint *)(param_1 + 0xb10) = *(uint *)(param_1 + 0xb10) | 0x18;
    *(uint *)(param_1 + 0xb10) = *(uint *)(param_1 + 0xb10) | 0x60000000;
    if (param_2 == 1) {
      *(undefined4 *)(param_1 + 0xb14) = param_3;
      *(uint *)(param_1 + 0xb00) = *(uint *)(param_1 + 0xb00) | 0x80008000;
    }
  }
  return 0;
}


// ===== FUN_08004ff4 @ 08004ff4

undefined4 FUN_08004ff4(int param_1,byte *param_2)

{
  uint uVar1;
  
  uVar1 = (uint)*param_2;
  if (param_2[1] == 1) {
    *(uint *)(param_1 + 0x900 + uVar1 * 0x20) =
         *(uint *)(param_1 + 0x900 + uVar1 * 0x20) & 0xffdfffff;
    if ((param_2[3] == 3) || (param_2[3] == 2)) {
      *(uint *)(param_1 + 0x900 + uVar1 * 0x20) =
           *(uint *)(param_1 + 0x900 + uVar1 * 0x20) | 0x10000000;
    }
  }
  else {
    *(uint *)(param_1 + 0xb00 + uVar1 * 0x20) =
         *(uint *)(param_1 + 0xb00 + uVar1 * 0x20) & 0xffdfffff;
    if ((param_2[3] == 3) || (param_2[3] == 2)) {
      *(uint *)(param_1 + 0xb00 + uVar1 * 0x20) =
           *(uint *)(param_1 + 0xb00 + uVar1 * 0x20) | 0x10000000;
    }
  }
  return 0;
}


// ===== FUN_08005082 @ 08005082

undefined4 FUN_08005082(int param_1,byte *param_2)

{
  uint uVar1;
  
  uVar1 = (uint)*param_2;
  if (param_2[1] == 1) {
    if (((*(uint *)(param_1 + 0x900 + uVar1 * 0x20) & 0x80000000) == 0) && (uVar1 != 0)) {
      *(uint *)(param_1 + 0x900 + uVar1 * 0x20) =
           *(uint *)(param_1 + 0x900 + uVar1 * 0x20) & 0xbfffffff;
    }
    *(uint *)(param_1 + 0x900 + uVar1 * 0x20) = *(uint *)(param_1 + 0x900 + uVar1 * 0x20) | 0x200000
    ;
  }
  else {
    if (((*(uint *)(param_1 + 0xb00 + uVar1 * 0x20) & 0x80000000) == 0) && (uVar1 != 0)) {
      *(uint *)(param_1 + 0xb00 + uVar1 * 0x20) =
           *(uint *)(param_1 + 0xb00 + uVar1 * 0x20) & 0xbfffffff;
    }
    *(uint *)(param_1 + 0xb00 + uVar1 * 0x20) = *(uint *)(param_1 + 0xb00 + uVar1 * 0x20) | 0x200000
    ;
  }
  return 0;
}


// ===== FUN_0800511c @ 0800511c

undefined4 FUN_0800511c(int param_1,byte *param_2,int param_3)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)*param_2;
  if (param_2[1] == 1) {
    if (*(int *)(param_2 + 0x14) == 0) {
      *(uint *)(param_1 + uVar2 * 0x20 + 0x910) =
           *(uint *)(param_1 + uVar2 * 0x20 + 0x910) & DAT_0800545c;
      *(uint *)(param_1 + uVar2 * 0x20 + 0x910) =
           *(uint *)(param_1 + uVar2 * 0x20 + 0x910) | 0x80000;
      *(uint *)(param_1 + uVar2 * 0x20 + 0x910) =
           *(uint *)(param_1 + uVar2 * 0x20 + 0x910) & 0xfff80000;
    }
    else {
      *(uint *)(param_1 + uVar2 * 0x20 + 0x910) =
           *(uint *)(param_1 + uVar2 * 0x20 + 0x910) & 0xfff80000;
      *(uint *)(param_1 + uVar2 * 0x20 + 0x910) =
           *(uint *)(param_1 + uVar2 * 0x20 + 0x910) & DAT_0800545c;
      *(uint *)(param_1 + uVar2 * 0x20 + 0x910) =
           ~DAT_0800545c &
           ((*(int *)(param_2 + 0x14) + *(uint *)(param_2 + 8)) - 1) / *(uint *)(param_2 + 8) <<
           0x13 | *(uint *)(param_1 + uVar2 * 0x20 + 0x910);
      *(uint *)(param_1 + uVar2 * 0x20 + 0x910) =
           *(uint *)(param_1 + uVar2 * 0x20 + 0x910) | *(uint *)(param_2 + 0x14) & 0x7ffff;
      if (param_2[3] == 1) {
        *(uint *)(param_1 + uVar2 * 0x20 + 0x910) =
             *(uint *)(param_1 + uVar2 * 0x20 + 0x910) & 0x9fffffff;
        *(uint *)(param_1 + uVar2 * 0x20 + 0x910) =
             *(uint *)(param_1 + uVar2 * 0x20 + 0x910) | 0x20000000;
      }
    }
    if (param_3 == 1) {
      if (*(int *)(param_2 + 0x10) != 0) {
        *(undefined4 *)(param_1 + uVar2 * 0x20 + 0x914) = *(undefined4 *)(param_2 + 0x10);
      }
      if (param_2[3] == 1) {
        if ((*(uint *)(param_1 + 0x808) & 0x100) == 0) {
          *(uint *)(param_1 + 0x900 + uVar2 * 0x20) =
               *(uint *)(param_1 + 0x900 + uVar2 * 0x20) | 0x20000000;
        }
        else {
          *(uint *)(param_1 + 0x900 + uVar2 * 0x20) =
               *(uint *)(param_1 + 0x900 + uVar2 * 0x20) | 0x10000000;
        }
      }
      *(uint *)(param_1 + 0x900 + uVar2 * 0x20) =
           *(uint *)(param_1 + 0x900 + uVar2 * 0x20) | 0x84000000;
    }
    else {
      *(uint *)(param_1 + 0x900 + uVar2 * 0x20) =
           *(uint *)(param_1 + 0x900 + uVar2 * 0x20) | 0x84000000;
      if (param_2[3] == 1) {
        if ((*(uint *)(param_1 + 0x808) & 0x100) == 0) {
          *(uint *)(param_1 + 0x900 + uVar2 * 0x20) =
               *(uint *)(param_1 + 0x900 + uVar2 * 0x20) | 0x20000000;
        }
        else {
          *(uint *)(param_1 + 0x900 + uVar2 * 0x20) =
               *(uint *)(param_1 + 0x900 + uVar2 * 0x20) | 0x10000000;
        }
        FUN_08005828(param_1,*(undefined4 *)(param_2 + 0xc),*param_2,*(undefined2 *)(param_2 + 0x14)
                     ,param_3);
      }
      else if (*(int *)(param_2 + 0x14) != 0) {
        *(uint *)(param_1 + 0x834) = *(uint *)(param_1 + 0x834) | 1 << (*param_2 & 0xf);
      }
    }
  }
  else {
    *(uint *)(param_1 + uVar2 * 0x20 + 0xb10) =
         *(uint *)(param_1 + uVar2 * 0x20 + 0xb10) & 0xfff80000;
    *(uint *)(param_1 + uVar2 * 0x20 + 0xb10) =
         *(uint *)(param_1 + uVar2 * 0x20 + 0xb10) & DAT_0800545c;
    if (*(int *)(param_2 + 0x14) == 0) {
      *(uint *)(param_1 + uVar2 * 0x20 + 0xb10) =
           *(uint *)(param_1 + uVar2 * 0x20 + 0xb10) | *(uint *)(param_2 + 8) & 0x7ffff;
      *(uint *)(param_1 + uVar2 * 0x20 + 0xb10) =
           *(uint *)(param_1 + uVar2 * 0x20 + 0xb10) | 0x80000;
    }
    else {
      uVar1 = ((*(int *)(param_2 + 0x14) + *(uint *)(param_2 + 8)) - 1) / *(uint *)(param_2 + 8);
      *(uint *)(param_1 + uVar2 * 0x20 + 0xb10) =
           *(uint *)(param_1 + uVar2 * 0x20 + 0xb10) | ~DAT_0800545c & uVar1 << 0x13;
      *(uint *)(param_1 + uVar2 * 0x20 + 0xb10) =
           *(uint *)(param_1 + uVar2 * 0x20 + 0xb10) |
           *(int *)(param_2 + 8) * (uVar1 & 0xffff) & 0x7ffff;
    }
    if ((param_3 == 1) && (*(int *)(param_2 + 0xc) != 0)) {
      *(undefined4 *)(param_1 + uVar2 * 0x20 + 0xb14) = *(undefined4 *)(param_2 + 0xc);
    }
    if (param_2[3] == 1) {
      if ((*(uint *)(param_1 + 0x808) & 0x100) == 0) {
        *(uint *)(param_1 + 0xb00 + uVar2 * 0x20) =
             *(uint *)(param_1 + 0xb00 + uVar2 * 0x20) | 0x20000000;
      }
      else {
        *(uint *)(param_1 + 0xb00 + uVar2 * 0x20) =
             *(uint *)(param_1 + 0xb00 + uVar2 * 0x20) | 0x10000000;
      }
    }
    *(uint *)(param_1 + 0xb00 + uVar2 * 0x20) =
         *(uint *)(param_1 + 0xb00 + uVar2 * 0x20) | 0x84000000;
  }
  return 0;
}


// ===== FUN_08005460 @ 08005460

undefined4 FUN_08005460(int param_1)

{
  *(uint *)(param_1 + 8) = *(uint *)(param_1 + 8) | 1;
  return 0;
}


// ===== FUN_08005470 @ 08005470

undefined4 FUN_08005470(int param_1)

{
  uint uVar1;
  
  uVar1 = 0;
  *(undefined4 *)(param_1 + 0x10) = 0x10;
  do {
    uVar1 = uVar1 + 1;
    if (DAT_08005498 < uVar1) {
      return 3;
    }
  } while ((*(uint *)(param_1 + 0x10) & 0x10) == 0x10);
  return 0;
}


// ===== FUN_0800549c @ 0800549c

undefined4 FUN_0800549c(int param_1,int param_2)

{
  uint uVar1;
  
  uVar1 = 0;
  *(uint *)(param_1 + 0x10) = param_2 << 6 | 0x20;
  do {
    uVar1 = uVar1 + 1;
    if (DAT_080054c8 < uVar1) {
      return 3;
    }
  } while ((*(uint *)(param_1 + 0x10) & 0x20) == 0x20);
  return 0;
}


// ===== FUN_080054cc @ 080054cc

undefined4 FUN_080054cc(int param_1)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar2 = *(uint *)(param_1 + 0x808) & 6;
  if (uVar2 == 0) {
    uVar1 = 0;
  }
  else if ((uVar2 == 2) || (uVar2 == 6)) {
    uVar1 = 2;
  }
  else {
    uVar1 = 0xf;
  }
  return uVar1;
}


// ===== FUN_080054f2 @ 080054f2

uint FUN_080054f2(int param_1)

{
  return *(uint *)(param_1 + 0x14) & 1;
}


// ===== FUN_080054fc @ 080054fc

void FUN_080054fc(int param_1,int param_2)

{
  uint *puVar1;
  int iVar2;
  
  if (param_1 != 0) {
    FUN_08000240(DAT_080055b4 + *DAT_080055b8,param_1,param_2);
    puVar1 = DAT_080055b8;
    *DAT_080055b8 = *DAT_080055b8 + param_2;
    if (3 < *puVar1) {
      switch(*DAT_080055b4) {
      case 0xa0:
      case 0xa1:
      case 0xa2:
      case 0xa3:
      case 0xa4:
        *DAT_080055bc = (uint)(byte)DAT_080055b4[1] << 2;
        break;
      default:
        iVar2 = FUN_08000296(DAT_080055b4,&DAT_080055c0,4);
        if (iVar2 != 0) {
          *DAT_080055b8 = 0;
          *DAT_080055c8 = 1;
          *DAT_080055cc = 0xe1;
        }
      }
    }
    if ((4 < *DAT_080055b8) && (iVar2 = FUN_08000296(DAT_080055b4,&DAT_080055c0,4), iVar2 == 0)) {
      *DAT_080055cc = 0xb0;
      *DAT_080055c8 = 2;
      *DAT_080055b8 = 0;
    }
    if ((*DAT_080055b8 == *DAT_080055bc) && (*DAT_080055bc != 0)) {
      *DAT_080055c8 = 1;
    }
  }
  return;
}


// ===== FUN_080055d0 @ 080055d0

uint FUN_080055d0(int param_1)

{
  return *(uint *)(param_1 + 0x818) & *(uint *)(param_1 + 0x81c) & 0xffff;
}


// ===== FUN_080055e4 @ 080055e4

uint FUN_080055e4(int param_1)

{
  return (*(uint *)(param_1 + 0x818) & *(uint *)(param_1 + 0x81c)) >> 0x10;
}


// ===== FUN_080055f8 @ 080055f8

uint FUN_080055f8(int param_1,uint param_2)

{
  return *(uint *)(param_1 + param_2 * 0x20 + 0x908) &
         (*(uint *)(param_1 + 0x810) | (*(uint *)(param_1 + 0x834) >> (param_2 & 0xf) & 1) << 7);
}


// ===== FUN_0800562a @ 0800562a

uint FUN_0800562a(int param_1,int param_2)

{
  return *(uint *)(param_1 + param_2 * 0x20 + 0xb08) & *(uint *)(param_1 + 0x814);
}


// ===== FUN_08005644 @ 08005644

uint FUN_08005644(int param_1)

{
  return *(uint *)(param_1 + 0x14) & *(uint *)(param_1 + 0x18);
}


// ===== FUN_0800564e @ 0800564e

void FUN_0800564e(int param_1,undefined4 *param_2,int param_3)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < param_3 + 3U >> 2; uVar1 = uVar1 + 1) {
    *param_2 = *(undefined4 *)(param_1 + 0x1000);
    param_2 = param_2 + 1;
  }
  return;
}


// ===== FUN_08005670 @ 08005670

undefined4 FUN_08005670(int param_1,int param_2)

{
  *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) & 0x9fffffff;
  if (param_2 == 1) {
    *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) | 0x20000000;
  }
  else {
    if (param_2 != 0) {
      return 1;
    }
    *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) | 0x40000000;
  }
  FUN_08000a30(0x32);
  return 0;
}


// ===== FUN_080056a6 @ 080056a6

undefined4 FUN_080056a6(int param_1,uint param_2)

{
  *(uint *)(param_1 + 0x800) = *(uint *)(param_1 + 0x800) & 0xfffff80f;
  *(uint *)(param_1 + 0x800) = *(uint *)(param_1 + 0x800) | (param_2 & 0x7f) << 4;
  return 0;
}


// ===== FUN_080056d0 @ 080056d0

undefined4 FUN_080056d0(int param_1,uint param_2)

{
  *(uint *)(param_1 + 0x800) = *(uint *)(param_1 + 0x800) | param_2;
  return 0;
}


// ===== FUN_080056e4 @ 080056e4

undefined4 FUN_080056e4(int param_1,uint param_2,int param_3)

{
  int iVar1;
  
  if (param_3 == 2) {
    if ((param_2 < DAT_080057a4) || (DAT_080057a8 <= param_2)) {
      if ((param_2 < DAT_080057a8) || (DAT_080057ac <= param_2)) {
        if ((param_2 < DAT_080057ac) || (DAT_080057b0 <= param_2)) {
          if ((param_2 < DAT_080057b0) || (DAT_080057b4 <= param_2)) {
            if ((param_2 < DAT_080057b4) || (DAT_080057b8 <= param_2)) {
              if ((param_2 < DAT_080057b8) || (DAT_080057bc <= param_2)) {
                if ((param_2 < DAT_080057bc) || (DAT_080057c0 <= param_2)) {
                  if ((param_2 < DAT_080057c0) || (DAT_080057c4 <= param_2)) {
                    if ((param_2 < DAT_080057c4) || (DAT_080057c8 <= param_2)) {
                      iVar1 = 6;
                    }
                    else {
                      iVar1 = 7;
                    }
                  }
                  else {
                    iVar1 = 8;
                  }
                }
                else {
                  iVar1 = 9;
                }
              }
              else {
                iVar1 = 10;
              }
            }
            else {
              iVar1 = 0xb;
            }
          }
          else {
            iVar1 = 0xc;
          }
        }
        else {
          iVar1 = 0xd;
        }
      }
      else {
        iVar1 = 0xe;
      }
    }
    else {
      iVar1 = 0xf;
    }
  }
  else if (param_3 == 0) {
    iVar1 = 9;
  }
  else {
    iVar1 = 9;
  }
  *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) & 0xffffc3ff;
  *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) | iVar1 << 10;
  return 0;
}


// ===== FUN_080057cc @ 080057cc

int FUN_080057cc(int param_1)

{
  int iVar1;
  uint uVar2;
  
  for (uVar2 = 0; uVar2 < 0xf; uVar2 = uVar2 + 1) {
    *(undefined4 *)(param_1 + uVar2 * 0x20 + 0x908) = 0xfb7f;
    *(undefined4 *)(param_1 + uVar2 * 0x20 + 0xb08) = 0xfb7f;
  }
  do {
    *(undefined4 *)(param_1 + 0x810) = 0;
    *(undefined4 *)(param_1 + 0x814) = 0;
    *(undefined4 *)(param_1 + 0x81c) = 0;
    iVar1 = FUN_08005470(param_1);
  } while ((iVar1 != 0) || (iVar1 = FUN_0800549c(param_1,0x10), iVar1 != 0));
  return iVar1;
}


// ===== FUN_08005828 @ 08005828

undefined4 FUN_08005828(int param_1,undefined4 *param_2,int param_3,int param_4,int param_5)

{
  uint uVar1;
  
  if (param_5 == 0) {
    for (uVar1 = 0; uVar1 < param_4 + 3U >> 2; uVar1 = uVar1 + 1) {
      *(undefined4 *)(param_1 + 0x1000 + param_3 * 0x1000) = *param_2;
      param_2 = param_2 + 1;
    }
  }
  return 0;
}


// ===== thunk_FUN_08005866 @ 08005864

void thunk_FUN_08005866(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}


// ===== FUN_08005866 @ 08005866

void FUN_08005866(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}


// ===== FUN_08005868 @ 08005868

void FUN_08005868(uint param_1)

{
  if (-1 < (int)param_1) {
    *(int *)((param_1 >> 5) * 4 + -0x1fff1f00) = 1 << (param_1 & 0x1f);
  }
  return;
}


// ===== FUN_08005884 @ 08005884

uint FUN_08005884(void)

{
  return (*DAT_08005890 & 0x7ff) >> 8;
}


// ===== FUN_08005894 @ 08005894

uint FUN_08005894(void)

{
  return (*DAT_080058a0 & 0x7ff) >> 8;
}


// ===== FUN_080058a4 @ 080058a4

void FUN_080058a4(uint param_1,uint param_2)

{
  if ((int)param_1 < 0) {
    *(char *)(DAT_080058c8 + ((param_1 & 0xf) - 4)) = (char)((param_2 & 0xf) << 4);
  }
  else {
    *(char *)(DAT_080058c4 + param_1) = (char)((param_2 & 0xf) << 4);
  }
  return;
}


// ===== FUN_080058cc @ 080058cc

void FUN_080058cc(uint param_1,uint param_2)

{
  if ((int)param_1 < 0) {
    *(char *)(DAT_080058f0 + ((param_1 & 0xf) - 4)) = (char)((param_2 & 0xf) << 4);
  }
  else {
    *(char *)(DAT_080058ec + param_1) = (char)((param_2 & 0xf) << 4);
  }
  return;
}


// ===== FUN_08005912 @ 08005912

void FUN_08005912(ushort *param_1,byte *param_2,int param_3)

{
  byte *pbVar1;
  byte bVar2;
  ushort uVar3;
  bool bVar4;
  
  if (param_3 != 0) {
    while (bVar4 = param_3 != 0, param_3 = param_3 + -1, bVar4) {
      pbVar1 = param_2 + 1;
      *param_1 = *param_1 ^ (ushort)*param_2 << 8;
      for (bVar2 = 0; param_2 = pbVar1, bVar2 < 8; bVar2 = bVar2 + 1) {
        if ((*param_1 & 0x8000) == 0) {
          uVar3 = *param_1 << 1;
        }
        else {
          uVar3 = *param_1 << 1 ^ 0x1021;
        }
        *param_1 = uVar3;
      }
    }
  }
  return;
}


// ===== FUN_0800595c @ 0800595c

void FUN_0800595c(int param_1)

{
  bool bVar1;
  int local_8;
  
  local_8 = param_1 * 5;
  do {
    bVar1 = local_8 != 0;
    local_8 = local_8 + -1;
  } while (bVar1);
  return;
}


// ===== FUN_08005972 @ 08005972

undefined4 FUN_08005972(uint param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_24;
  undefined4 local_20 [2];
  uint local_18;
  undefined4 local_14;
  undefined4 local_10;
  
  uVar2 = 0;
  FUN_08000272(local_20,0x14);
  local_24 = 0;
  if (param_1 < 4) {
    uVar2 = 0xffffffff;
  }
  else {
    local_20[0] = 0;
    local_10 = 2;
    local_14 = 1;
    local_18 = param_1;
    iVar1 = FUN_08000a58(local_20,&local_24);
    if (iVar1 != 0) {
      uVar2 = 0xffffffff;
    }
  }
  return uVar2;
}


// ===== FUN_080059b0 @ 080059b0

void FUN_080059b0(void)

{
  FUN_08000b9c();
  return;
}


// ===== FUN_080059b8 @ 080059b8

undefined4 FUN_080059b8(uint param_1,int param_2,uint param_3)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  
  piVar1 = DAT_08005a44;
  iVar4 = 0;
  uVar5 = param_1 + param_3;
  if ((param_1 < DAT_08005a3c) || (DAT_08005a40 <= param_1)) {
    uVar2 = 0xffffffff;
  }
  else if (((param_2 == 0) || (param_3 == 0)) || ((param_3 & 3) != 0)) {
    uVar2 = 0xffffffff;
  }
  else {
    *DAT_08005a44 = *DAT_08005a44 + 1;
    if (1 < *piVar1) {
      *piVar1 = *piVar1 + 1;
    }
    for (; param_1 < uVar5; param_1 = param_1 + 4) {
      iVar3 = FUN_08000b04(2,param_1,*(undefined4 *)(param_2 + iVar4),0);
      if (iVar3 != 0) {
        return 0xffffffff;
      }
      iVar4 = iVar4 + 4;
    }
    uVar2 = 0;
  }
  return uVar2;
}


// ===== FUN_08005a98 @ 08005a98

int FUN_08005a98(undefined4 *param_1)

{
  int *piVar1;
  undefined4 *puVar2;
  byte *pbVar3;
  int iVar4;
  undefined4 *puVar5;
  
  iVar4 = 0;
  pbVar3 = (byte *)*param_1;
  puVar2 = param_1;
  puVar5 = (undefined4 *)0x0;
  if (pbVar3 != (byte *)0x0) {
    piVar1 = (int *)FUN_0800022c();
    puVar2 = (undefined4 *)(uint)(*(char *)(*piVar1 + (uint)*pbVar3) == ' ');
    puVar5 = puVar2;
  }
  while (puVar5 != (undefined4 *)0x0) {
    if (pbVar3 != (byte *)0x0) {
      puVar2 = (undefined4 *)(*pbVar3 - 0x30);
      iVar4 = (int)puVar2 + iVar4 * 10;
      pbVar3 = pbVar3 + 1;
      if (pbVar3 != (byte *)0x0) {
        piVar1 = (int *)FUN_0800022c();
        puVar2 = (undefined4 *)(uint)(*(char *)(*piVar1 + (uint)*pbVar3) == ' ');
      }
    }
    piVar1 = (int *)FUN_0800022c(puVar2);
    puVar2 = (undefined4 *)(uint)(*(char *)(*piVar1 + (uint)*pbVar3) == ' ');
    puVar5 = puVar2;
  }
  *param_1 = pbVar3;
  return iVar4;
}


// ===== FUN_08005b08 @ 08005b08

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08005b08(uint *param_1)

{
  FUN_08006040(s___stack___x_08005b37 + 1,*param_1 & _DAT_08005b34);
  FUN_08006580();
  *DAT_08005b48 = param_1[1];
  FUN_0800019c(param_1);
  (*(code *)*DAT_08005b48)();
  return;
}


// ===== FUN_08005b4c @ 08005b4c

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08005b4c(void)

{
  int iVar1;
  
  FUN_08000f58();
  FUN_08002df4();
  FUN_08002718();
  FUN_080003d0();
  FUN_080028c4();
  FUN_08002818();
  FUN_080027e0();
  FUN_08002980();
  iVar1 = FUN_0800036a();
  if (iVar1 == 0) {
    for (iVar1 = 0; iVar1 < 10; iVar1 = iVar1 + 1) {
      FUN_08000a30(100);
      if ((*DAT_08005c10 == '\x02') || (*DAT_08005c14 == 2)) {
        if (*DAT_08005c10 == '\x02') {
          *DAT_08005c18 = '\x01';
        }
        if (*DAT_08005c14 == 2) {
          *DAT_08005c18 = '\x02';
        }
        goto LAB_08005be8;
      }
    }
    if ((int)(*_DAT_08005c1c << 3) < 0) {
      *_DAT_08005c1c = *_DAT_08005c1c | 0x1000000;
      FUN_08006040(s___software_reset__now_in_bootloa_08005c1f + 1);
      FUN_08006590(s___software_reset__now_in_bootloa_08005c1f + 1);
    }
    else {
      FUN_08005b08(*_DAT_08005c48);
      FUN_08006040(s_jump_to_app_failed_08005c4b + 1);
    }
  }
LAB_08005be8:
  do {
    do {
      if ((*DAT_08005c10 != '\0') || (*DAT_08005c18 == '\x01')) {
        FUN_08005e28();
      }
    } while ((*DAT_08005c14 == 0) && (*DAT_08005c18 != '\x02'));
    FUN_08006368();
  } while( true );
}


// ===== FUN_08005cd0 @ 08005cd0

void FUN_08005cd0(int param_1)

{
  DAT_08005cec[1] = param_1;
  do {
  } while (-1 < *DAT_08005cec << 0x19);
  return;
}


// ===== FUN_08005cf0 @ 08005cf0

void FUN_08005cf0(uint param_1,uint param_2,undefined4 *param_3)

{
  bool bVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined1 auStack_50 [19];
  undefined1 auStack_3d [33];
  
  FUN_08000240(auStack_50,s_0123456789ABCDEF_08005da4,0x14);
  for (iVar3 = 0; iVar3 < 0x20; iVar3 = iVar3 + 1) {
    auStack_3d[iVar3 + 1] = 0x30;
  }
  if (((param_3[6] == 0) && (param_2 == 10)) && ((int)param_1 < 0)) {
    bVar1 = true;
    param_1 = -param_1;
  }
  else {
    bVar1 = false;
  }
  iVar3 = 0;
  do {
    iVar4 = iVar3;
    auStack_3d[iVar4 + 1] = auStack_50[param_1 - param_2 * (param_1 / param_2)];
    iVar3 = iVar4 + 1;
    param_1 = param_1 / param_2;
  } while (param_1 != 0);
  if (bVar1) {
    auStack_3d[iVar4 + 2] = 0x2d;
    iVar3 = iVar4 + 2;
  }
  auStack_3d[iVar3 + 1] = 0;
  uVar2 = FUN_08000288(auStack_3d + 1);
  *param_3 = uVar2;
  FUN_08005e00(param_3[5] == 0,param_3);
  while (auStack_3d + 1 <= auStack_3d + iVar3) {
    FUN_08005cd0(auStack_3d[iVar3]);
    iVar3 = iVar3 + -1;
  }
  FUN_08005e00(param_3[5],param_3);
  return;
}


// ===== FUN_08005db8 @ 08005db8

void FUN_08005db8(char *param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  
  if (param_1 != (char *)0x0) {
    uVar1 = FUN_08000288(param_1);
    *param_2 = uVar1;
  }
  FUN_08005e00(param_2[5] == 0,param_2);
  while ((*param_1 != '\0' && (param_2[2] != 0))) {
    param_2[2] = param_2[2] + -1;
    FUN_08005cd0(*param_1);
    param_1 = param_1 + 1;
  }
  FUN_08005e00(param_2[5],param_2);
  return;
}


// ===== FUN_08005e00 @ 08005e00

void FUN_08005e00(int param_1,int *param_2)

{
  int *extraout_r2;
  int iVar1;
  int extraout_r3;
  
  if (((param_2[4] != 0) && (param_1 != 0)) && (*param_2 < param_2[1])) {
    iVar1 = *param_2;
    while (iVar1 < param_2[1]) {
      FUN_08005cd0((char)param_2[3]);
      param_2 = extraout_r2;
      iVar1 = extraout_r3 + 1;
    }
  }
  return;
}


// ===== FUN_08005e28 @ 08005e28

undefined8 FUN_08005e28(void)

{
  int *piVar1;
  undefined3 uVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  
  local_10 = 0;
  local_18 = 0;
  local_14 = 0;
  if (*DAT_08006028 == '\x02') {
    local_18._0_3_ = CONCAT12((char)*DAT_0800602c,0x5c4);
    local_18 = (uint)(uint3)local_18;
    local_10 = 0;
    FUN_08005912(&local_10,&local_18,3);
    local_18 = CONCAT13((char)local_10,(uint3)local_18);
    local_14 = CONCAT31(local_14._1_3_,(char)((uint)local_10 >> 8));
    FUN_08006224(&local_18,5);
    *DAT_0800602c = 0xe0;
    uVar4 = 0;
    *DAT_08006028 = '\0';
    *DAT_08006030 = 0;
  }
  else if (*DAT_08006028 == '\x01') {
    if (*DAT_0800602c == 0xe0) {
      *DAT_08006030 = 0;
      *DAT_08006028 = '\0';
      FUN_08005912(&local_10,DAT_08006038,*DAT_08006034 + -2);
      piVar1 = DAT_0800602c;
      uVar2 = local_18._1_3_;
      uVar3 = local_18._3_1_;
      if ((short)local_10 ==
          CONCAT11(DAT_08006038[*DAT_08006034 + -1],DAT_08006038[*DAT_08006034 + -2])) {
        switch(*DAT_08006038) {
        case 0xa0:
          local_18 = CONCAT31(uVar2,0xc0);
          local_18._0_3_ = CONCAT12((char)*DAT_0800602c,(undefined2)local_18);
          local_18 = CONCAT13(uVar3,(uint3)local_18);
          break;
        case 0xa1:
          local_18 = CONCAT31(uVar2,0xc1);
          iVar5 = FUN_080062b4();
          piVar1 = DAT_0800602c;
          *DAT_0800602c = iVar5;
          local_18._0_3_ = CONCAT12((char)*piVar1,(undefined2)local_18);
          break;
        case 0xa2:
          local_18 = CONCAT31(uVar2,0xc2);
          iVar5 = FUN_08006260();
          piVar1 = DAT_0800602c;
          *DAT_0800602c = iVar5;
          local_18._0_3_ = CONCAT12((char)*piVar1,(undefined2)local_18);
          break;
        case 0xa3:
          local_18 = CONCAT31(uVar2,0xc3);
          iVar5 = FUN_0800632c();
          piVar1 = DAT_0800602c;
          *DAT_0800602c = iVar5;
          local_18._0_3_ = CONCAT12((char)*piVar1,(undefined2)local_18);
          break;
        case 0xa4:
          FUN_08005b08(DAT_0800603c);
          break;
        default:
          *DAT_0800602c = 0xe1;
          local_18._0_3_ = CONCAT12((char)*piVar1,(undefined2)local_18);
        }
        local_10 = 0;
        local_18._0_2_ = CONCAT11(5,(undefined1)local_18);
        FUN_08005912(&local_10,&local_18,4);
        local_18 = CONCAT13((char)local_10,(uint3)local_18);
        local_14 = CONCAT31(local_14._1_3_,(char)((uint)local_10 >> 8));
        FUN_08006224(&local_18,5);
        uVar4 = 0;
      }
      else {
        local_18 = CONCAT13(local_18._3_1_,0xe405c0);
        local_10 = 0;
        FUN_08005912(&local_10,&local_18,3);
        local_18 = CONCAT13((char)local_10,(uint3)local_18);
        local_14 = CONCAT31(local_14._1_3_,(char)((uint)local_10 >> 8));
        FUN_08006224(&local_18,5);
        uVar4 = 0xffffffff;
      }
    }
    else {
      local_18._0_3_ = CONCAT12((char)*DAT_0800602c,0x5c0);
      local_18 = (uint)(uint3)local_18;
      local_10 = 0;
      FUN_08005912(&local_10,&local_18,3);
      local_18 = CONCAT13((char)local_10,(uint3)local_18);
      local_14 = CONCAT31(local_14._1_3_,(char)((uint)local_10 >> 8));
      FUN_08006224(&local_18,5);
      *DAT_0800602c = 0xe0;
      *DAT_08006028 = '\0';
      *DAT_08006030 = 0;
      uVar4 = 0xffffffff;
    }
  }
  else {
    uVar4 = 0xffffffff;
  }
  return CONCAT44(local_18,uVar4);
}


// ===== FUN_08006040 @ 08006040

void FUN_08006040(byte *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  undefined1 uVar2;
  bool bVar3;
  int *piVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  int unaff_r5;
  byte *local_44;
  undefined4 *local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined1 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_c;
  undefined4 uStack_8;
  undefined4 uStack_4;
  
  local_40 = &local_c;
  local_44 = param_1;
  local_c = param_2;
  uStack_8 = param_3;
  uStack_4 = param_4;
  do {
    while( true ) {
      if ((local_44 == (byte *)0x0) || (*local_44 == 0)) {
        return;
      }
      if (*local_44 == 0x25) break;
      FUN_08005cd0(*local_44);
      local_44 = local_44 + 1;
    }
    bVar3 = false;
    local_24 = 0;
    local_28 = 0;
    local_2c = 0;
    local_30 = 0x20;
    local_34 = 0x7fff;
    local_38 = 0;
    local_3c = 0;
    do {
      while( true ) {
        if (local_44 != (byte *)0x0) {
          local_44 = local_44 + 1;
        }
        if (local_44 == (byte *)0x0) {
          bVar1 = MasterStackPointer;
        }
        else {
          bVar1 = *local_44;
        }
        uVar7 = (uint)bVar1;
        piVar4 = (int *)FUN_0800022c();
        if (*(char *)(*piVar4 + uVar7) != ' ') break;
        if (bVar3) {
          local_34 = FUN_08005a98(&local_44);
        }
        else {
          if (uVar7 == 0x30) {
            local_30 = 0x30;
          }
          if (local_44 != (byte *)0x0) {
            local_38 = FUN_08005a98(&local_44);
          }
          local_2c = 1;
        }
        if (local_44 != (byte *)0x0) {
          local_44 = local_44 + -1;
        }
      }
      iVar5 = FUN_08000234(uVar7);
      if (iVar5 == 100) goto LAB_08006150;
      if (iVar5 < 0x65) {
        if (iVar5 == 0x58) {
LAB_08006166:
          local_24 = 1;
          uVar6 = *local_40;
          local_40 = local_40 + 1;
          FUN_08005cf0(uVar6,0x10,&local_3c);
          unaff_r5 = 1;
        }
        else if (iVar5 < 0x59) {
          if (iVar5 == 0x25) {
            FUN_08005cd0(0x25);
            unaff_r5 = 1;
          }
          else if (iVar5 == 0x2d) {
            local_28 = 1;
            unaff_r5 = 0;
          }
          else {
            if (iVar5 != 0x2e) goto LAB_080061f0;
            bVar3 = true;
            unaff_r5 = 0;
          }
        }
        else if (iVar5 == 0x5c) {
          bVar1 = *local_44;
          if (bVar1 == 0x61) {
            FUN_08005cd0(7);
          }
          else if (bVar1 == 0x68) {
            FUN_08005cd0(8);
          }
          else if (bVar1 == 0x6e) {
            FUN_08005cd0(0xd);
            FUN_08005cd0(10);
          }
          else if (bVar1 == 0x72) {
            FUN_08005cd0(0xd);
          }
          else {
            FUN_08005cd0(*local_44);
          }
          local_44 = local_44 + 1;
          unaff_r5 = 0;
        }
        else {
          if (iVar5 != 99) goto LAB_080061f0;
          uVar2 = *(undefined1 *)local_40;
          local_40 = local_40 + 1;
          FUN_08005cd0(uVar2);
          unaff_r5 = 1;
        }
      }
      else if (iVar5 == 0x73) {
        uVar6 = *local_40;
        local_40 = local_40 + 1;
        FUN_08005db8(uVar6,&local_3c);
      }
      else if (iVar5 < 0x74) {
        if (iVar5 == 0x69) {
LAB_08006150:
          uVar6 = *local_40;
          local_40 = local_40 + 1;
          FUN_08005cf0(uVar6,10,&local_3c);
          unaff_r5 = 1;
        }
        else {
          if (iVar5 != 0x6c) {
            if (iVar5 == 0x70) goto LAB_08006166;
            goto LAB_080061f0;
          }
          unaff_r5 = 0;
        }
      }
      else {
        if (iVar5 == 0x75) {
          local_24 = 1;
          goto LAB_08006150;
        }
        if (iVar5 == 0x78) goto LAB_08006166;
LAB_080061f0:
        unaff_r5 = 1;
      }
    } while (unaff_r5 != 1);
    if (local_44 != (byte *)0x0) {
      local_44 = local_44 + 1;
    }
  } while( true );
}


// ===== FUN_08006224 @ 08006224

undefined4 FUN_08006224(byte *param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  
  if ((param_1 == (byte *)0x0) || (param_2 == 0)) {
    uVar1 = 1;
  }
  else {
    for (iVar2 = 0; iVar2 < param_2; iVar2 = iVar2 + 1) {
      DAT_0800625c[1] = (uint)*param_1;
      do {
      } while (-1 < *DAT_0800625c << 0x19);
      param_1 = param_1 + 1;
    }
    uVar1 = 0;
  }
  return uVar1;
}


// ===== FUN_08006260 @ 08006260

/* WARNING: Removing unreachable block (ram,0x0800628c) */

undefined4 FUN_08006260(void)

{
  byte bVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  
  iVar3 = DAT_080062a8;
  uVar4 = *(uint *)(DAT_080062a8 + -4);
  bVar1 = *(byte *)(DAT_080062a8 + -5);
  if ((uVar4 < DAT_080062ac) || (DAT_080062b0 < uVar4)) {
    uVar2 = 0xe6;
  }
  else {
    FUN_080059b0();
    iVar3 = FUN_080059b8(uVar4,iVar3,(uint)bVar1 * 4 + -8);
    if (iVar3 == 0) {
      uVar2 = 0xe0;
    }
    else {
      uVar2 = 0xe3;
    }
  }
  return uVar2;
}


// ===== FUN_080062b4 @ 080062b4

undefined4 FUN_080062b4(void)

{
  undefined4 uVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  
  iVar4 = *(int *)(DAT_0800631c + 2);
  iVar5 = *(int *)(DAT_0800631c + 6);
  *DAT_08006320 = iVar4;
  *DAT_08006324 = iVar5;
  if (*DAT_08006320 == DAT_08006328) {
    uVar2 = FUN_08000954(iVar4);
    uVar3 = FUN_08000954(iVar4 + iVar5);
    if ((uVar2 < 4) || (7 < uVar2)) {
      uVar1 = 0xe6;
    }
    else {
      FUN_080059b0();
      FUN_08000566();
      for (; uVar2 <= uVar3; uVar2 = uVar2 + 1) {
        iVar4 = FUN_08005972(uVar2);
        if (iVar4 != 0) {
          return 0xe2;
        }
      }
      uVar1 = 0xe0;
    }
  }
  else {
    uVar1 = 0xe6;
  }
  return uVar1;
}


// ===== FUN_0800632c @ 0800632c

undefined4 FUN_0800632c(void)

{
  undefined4 uVar1;
  uint uVar2;
  uint local_10;
  
  uVar2 = *(uint *)(DAT_0800635c + 2);
  local_10 = 0;
  FUN_08005912(&local_10,*DAT_08006364,*DAT_08006360);
  if ((local_10 & 0xffff) == uVar2) {
    FUN_080003b0();
    uVar1 = 0xe0;
  }
  else {
    uVar1 = 0xe4;
  }
  return uVar1;
}


// ===== FUN_08006368 @ 08006368

undefined8 FUN_08006368(void)

{
  int *piVar1;
  undefined3 uVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  
  local_10 = 0;
  local_18 = 0;
  local_14 = 0;
  if (*DAT_08006568 == 2) {
    local_18._0_3_ = CONCAT12((char)*DAT_0800656c,0x5c4);
    local_18 = (uint)(uint3)local_18;
    local_10 = 0;
    FUN_08005912(&local_10,&local_18,3);
    local_18 = CONCAT13((char)local_10,(uint3)local_18);
    local_14 = CONCAT31(local_14._1_3_,(char)((uint)local_10 >> 8));
    FUN_08006772(&local_18,5);
    *DAT_0800656c = 0xe0;
    uVar4 = 0;
    *DAT_08006568 = 0;
    *DAT_08006570 = 0;
  }
  else if (*DAT_08006568 == 1) {
    if (*DAT_0800656c == 0xe0) {
      *DAT_08006570 = 0;
      *DAT_08006568 = 0;
      FUN_08005912(&local_10,DAT_08006578,*DAT_08006574 + -2);
      piVar1 = DAT_0800656c;
      uVar2 = local_18._1_3_;
      uVar3 = local_18._3_1_;
      if ((short)local_10 ==
          CONCAT11(DAT_08006578[*DAT_08006574 + -1],DAT_08006578[*DAT_08006574 + -2])) {
        switch(*DAT_08006578) {
        case 0xa0:
          local_18 = CONCAT31(uVar2,0xc0);
          local_18._0_3_ = CONCAT12((char)*DAT_0800656c,(undefined2)local_18);
          local_18 = CONCAT13(uVar3,(uint3)local_18);
          break;
        case 0xa1:
          local_18 = CONCAT31(uVar2,0xc1);
          iVar5 = FUN_080062b4();
          piVar1 = DAT_0800656c;
          *DAT_0800656c = iVar5;
          local_18._0_3_ = CONCAT12((char)*piVar1,(undefined2)local_18);
          break;
        case 0xa2:
          local_18 = CONCAT31(uVar2,0xc2);
          iVar5 = FUN_08006260();
          piVar1 = DAT_0800656c;
          *DAT_0800656c = iVar5;
          local_18._0_3_ = CONCAT12((char)*piVar1,(undefined2)local_18);
          break;
        case 0xa3:
          local_18 = CONCAT31(uVar2,0xc3);
          iVar5 = FUN_0800632c();
          piVar1 = DAT_0800656c;
          *DAT_0800656c = iVar5;
          local_18._0_3_ = CONCAT12((char)*piVar1,(undefined2)local_18);
          break;
        case 0xa4:
          FUN_08005b08(DAT_0800657c);
          break;
        default:
          *DAT_0800656c = 0xe1;
          local_18._0_3_ = CONCAT12((char)*piVar1,(undefined2)local_18);
        }
        local_10 = 0;
        local_18._0_2_ = CONCAT11(5,(undefined1)local_18);
        FUN_08005912(&local_10,&local_18,4);
        local_18 = CONCAT13((char)local_10,(uint3)local_18);
        local_14 = CONCAT31(local_14._1_3_,(char)((uint)local_10 >> 8));
        FUN_08006772(&local_18,5);
        uVar4 = 0;
      }
      else {
        local_18 = CONCAT13(local_18._3_1_,0xe405c0);
        local_10 = 0;
        FUN_08005912(&local_10,&local_18,3);
        local_18 = CONCAT13((char)local_10,(uint3)local_18);
        local_14 = CONCAT31(local_14._1_3_,(char)((uint)local_10 >> 8));
        FUN_08006772(&local_18,5);
        uVar4 = 0xffffffff;
      }
    }
    else {
      local_18._0_3_ = CONCAT12((char)*DAT_0800656c,0x5c0);
      local_18 = (uint)(uint3)local_18;
      local_10 = 0;
      FUN_08005912(&local_10,&local_18,3);
      local_18 = CONCAT13((char)local_10,(uint3)local_18);
      local_14 = CONCAT31(local_14._1_3_,(char)((uint)local_10 >> 8));
      FUN_08006772(&local_18,5);
      *DAT_0800656c = 0xe0;
      *DAT_08006568 = 0;
      *DAT_08006570 = 0;
      uVar4 = 0xffffffff;
    }
  }
  else {
    uVar4 = 0xffffffff;
  }
  return CONCAT44(local_18,uVar4);
}


// ===== FUN_08006580 @ 08006580

void FUN_08006580(void)

{
  FUN_08003942(DAT_0800658c);
  return;
}


// ===== FUN_08006590 @ 08006590

void FUN_08006590(byte *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  undefined1 uVar2;
  bool bVar3;
  int *piVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  int unaff_r5;
  byte *local_44;
  undefined4 *local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined1 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_c;
  undefined4 uStack_8;
  undefined4 uStack_4;
  
  local_40 = &local_c;
  local_44 = param_1;
  local_c = param_2;
  uStack_8 = param_3;
  uStack_4 = param_4;
  do {
    while( true ) {
      if ((local_44 == (byte *)0x0) || (*local_44 == 0)) {
        return;
      }
      if (*local_44 == 0x25) break;
      FUN_08006782(*local_44);
      local_44 = local_44 + 1;
    }
    bVar3 = false;
    local_24 = 0;
    local_28 = 0;
    local_2c = 0;
    local_30 = 0x20;
    local_34 = 0x7fff;
    local_38 = 0;
    local_3c = 0;
    do {
      while( true ) {
        if (local_44 != (byte *)0x0) {
          local_44 = local_44 + 1;
        }
        if (local_44 == (byte *)0x0) {
          bVar1 = MasterStackPointer;
        }
        else {
          bVar1 = *local_44;
        }
        uVar7 = (uint)bVar1;
        piVar4 = (int *)FUN_0800022c();
        if (*(char *)(*piVar4 + uVar7) != ' ') break;
        if (bVar3) {
          local_34 = FUN_08005a98(&local_44);
        }
        else {
          if (uVar7 == 0x30) {
            local_30 = 0x30;
          }
          if (local_44 != (byte *)0x0) {
            local_38 = FUN_08005a98(&local_44);
          }
          local_2c = 1;
        }
        if (local_44 != (byte *)0x0) {
          local_44 = local_44 + -1;
        }
      }
      iVar5 = FUN_08000234(uVar7);
      if (iVar5 == 100) goto LAB_080066a0;
      if (iVar5 < 0x65) {
        if (iVar5 == 0x58) {
LAB_080066b6:
          local_24 = 1;
          uVar6 = *local_40;
          local_40 = local_40 + 1;
          FUN_08005cf0(uVar6,0x10,&local_3c);
          unaff_r5 = 1;
        }
        else if (iVar5 < 0x59) {
          if (iVar5 == 0x25) {
            FUN_08006782(0x25);
            unaff_r5 = 1;
          }
          else if (iVar5 == 0x2d) {
            local_28 = 1;
            unaff_r5 = 0;
          }
          else {
            if (iVar5 != 0x2e) goto LAB_08006740;
            bVar3 = true;
            unaff_r5 = 0;
          }
        }
        else if (iVar5 == 0x5c) {
          bVar1 = *local_44;
          if (bVar1 == 0x61) {
            FUN_08006782(7);
          }
          else if (bVar1 == 0x68) {
            FUN_08006782(8);
          }
          else if (bVar1 == 0x6e) {
            FUN_08006782(0xd);
            FUN_08006782(10);
          }
          else if (bVar1 == 0x72) {
            FUN_08006782(0xd);
          }
          else {
            FUN_08006782(*local_44);
          }
          local_44 = local_44 + 1;
          unaff_r5 = 0;
        }
        else {
          if (iVar5 != 99) goto LAB_08006740;
          uVar2 = *(undefined1 *)local_40;
          local_40 = local_40 + 1;
          FUN_08006782(uVar2);
          unaff_r5 = 1;
        }
      }
      else if (iVar5 == 0x73) {
        uVar6 = *local_40;
        local_40 = local_40 + 1;
        FUN_08005db8(uVar6,&local_3c);
      }
      else if (iVar5 < 0x74) {
        if (iVar5 == 0x69) {
LAB_080066a0:
          uVar6 = *local_40;
          local_40 = local_40 + 1;
          FUN_08005cf0(uVar6,10,&local_3c);
          unaff_r5 = 1;
        }
        else {
          if (iVar5 != 0x6c) {
            if (iVar5 == 0x70) goto LAB_080066b6;
            goto LAB_08006740;
          }
          unaff_r5 = 0;
        }
      }
      else {
        if (iVar5 == 0x75) {
          local_24 = 1;
          goto LAB_080066a0;
        }
        if (iVar5 == 0x78) goto LAB_080066b6;
LAB_08006740:
        unaff_r5 = 1;
      }
    } while (unaff_r5 != 1);
    if (local_44 != (byte *)0x0) {
      local_44 = local_44 + 1;
    }
  } while( true );
}


// ===== FUN_08006772 @ 08006772

void FUN_08006772(undefined4 param_1,undefined2 param_2)

{
  FUN_08000668(param_1,param_2);
  return;
}


// ===== FUN_08006782 @ 08006782

void FUN_08006782(undefined4 param_1)

{
  undefined4 uStack_8;
  
  uStack_8 = param_1;
  FUN_08000668(&uStack_8,1);
  return;
}


