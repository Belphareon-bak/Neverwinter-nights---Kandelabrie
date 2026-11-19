#include "hvd_core"

void main()
{
    if (!HVD_Run()) HVD_NewRun();
    int count = 0;
    object area = GetFirstArea();
    while (GetIsObjectValid(area))
    {
        ++count;
        area = GetNextArea();
    }
    PrintString("HVEZDARNA loaded " + IntToString(count) + " areas; run " + IntToString(HVD_Run()));
}
