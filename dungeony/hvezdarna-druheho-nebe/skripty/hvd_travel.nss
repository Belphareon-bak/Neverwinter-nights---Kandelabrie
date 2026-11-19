#include "hvd_core"

void main()
{
    object player = GetEnteringObject();
    if (!HVD_IsPlayer(player)) return;
    object module = HVD_Module();
    string requirement = GetLocalString(OBJECT_SELF, "require");
    if (requirement != "" && !GetLocalInt(module, requirement))
    {
        string hint = "Servisní průlez se otevírá z druhé strany.";
        if (requirement == "hvd_aligned") hint = "V oblouku chybí světlo. Seřiď optiku v kopuli.";
        if (requirement == "hvd_gate_open") hint = "Bránu otevře soustava tří sloupů. Spoušť a závora jsou pod schody.";
        if (requirement == "hvd_won") hint = "Sestup se otevře, až ustane odraz poslední lucerny.";
        if (requirement == "hvd_study_link") hint = "Ve spáře je vidět zadní clona. Z druhé strany ji drží převod.";
        if (requirement == "hvd_eave_open") hint = "Kamenný kryt drží táhlo pod západní opěrou.";
        SendMessageToPC(player, hint);
        return;
    }
    string flag = GetLocalString(OBJECT_SELF, "flag");
    if (flag != "") SetLocalInt(module, flag, TRUE);
    HVD_Jump(player, GetLocalString(OBJECT_SELF, "target"));
}
