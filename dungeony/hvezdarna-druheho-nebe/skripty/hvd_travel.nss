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
        if (requirement == "hvd_gate_open") hint = "Brána se zjeví, až se rozsvítí všechny tři správné patice.";
        if (requirement == "hvd_won") hint = "Sestup se otevře, až ustane odraz poslední lucerny.";
        SendMessageToPC(player, hint);
        return;
    }
    string flag = GetLocalString(OBJECT_SELF, "flag");
    if (flag != "") SetLocalInt(module, flag, TRUE);
    HVD_Jump(player, GetLocalString(OBJECT_SELF, "target"));
}
