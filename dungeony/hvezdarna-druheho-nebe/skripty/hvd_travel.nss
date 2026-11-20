#include "hvd_core"

void main()
{
    object player = GetEnteringObject();
    if (!HVD_IsPlayer(player)) return;
    object module = HVD_Module();
    string requirement = GetLocalString(OBJECT_SELF, "require");
    int minimum = GetLocalInt(OBJECT_SELF, "minimum_level");
    if (requirement != "" && !GetLocalInt(module, requirement))
    {
        if (minimum) return;
        string hint = "Kamenný průchod je uzavřený.";
        if (requirement == "hvd_aligned") hint = "V oblouku chybí světlo. Seřiď optiku v kopuli.";
        if (requirement == "hvd_gate_open") hint = "Bránu otevře soustava tří sloupů. Spoušť a závora jsou pod schody.";
        SendMessageToPC(player, hint);
        return;
    }
    if (GetHitDice(player) < minimum)
    {
        SendMessageToPC(player, "Služební průchod je přístupný od " + IntToString(minimum) + ". úrovně.");
        return;
    }
    HVD_Jump(player, GetLocalString(OBJECT_SELF, "target"));
}
