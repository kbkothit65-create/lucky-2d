import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import flet as ft
from datetime import datetime, timedelta
from supabase import create_client, Client

# ----------------------------------------------------
# 🔗 SUPABASE CONNECTION SETTINGS
# ----------------------------------------------------
SUPABASE_URL = "https://clnkkaxojracvgozbtnl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNsbmtrYXhvanJhY3Znb3pidG5sIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NDcyODgyMiwiZXhwIjoyMTAwMzA0ODIyfQ.6OdNGDMi4C01iGllLENXmXSilhN8JLjQxkqaIEQn7hk"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🔐 ADMIN ONLY PASSCODE
ADMIN_PIN = "Lucky@2D"

# Global Current User Session
current_user = {
    "phone": "",
    "name": ""
}

def main(page: ft.Page):
    page.title = "Lucky 2D"
    page.window.width = 390
    page.window.height = 800
    page.window.resizable = False
    page.padding = 15
    page.theme_mode = ft.ThemeMode.DARK

    selected_numbers = []

    def go_back(e=None):
        if len(page.views) > 1:
            page.views.pop()
            page.update()

    # ----------------------------------------------------
    # 💰 FETCH USER BALANCE
    # ----------------------------------------------------
    def get_user_balance():
        if not current_user["phone"]:
            return 0
        try:
            res = supabase.table("users").select("balance").eq("id", current_user["phone"]).execute()
            if res.data:
                return res.data[0]["balance"]
        except Exception as ex:
            print("Database Balance Error:", ex)
        return 0

    wallet_text = ft.Text("0 Ks", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
    user_name_text = ft.Text("", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    user_phone_text = ft.Text("", size=10, color=ft.Colors.GREY_400)

    def refresh_wallet_ui():
        bal = get_user_balance()
        wallet_text.value = f"{bal:,} Ks"
        user_name_text.value = current_user["name"]
        user_phone_text.value = current_user["phone"]
        page.update()

    # ----------------------------------------------------
    # 🔑 AUTHENTICATION VIEW
    # ----------------------------------------------------
    def show_login_signup_view():
        phone_input = ft.TextField(
            label="ဖုန်းနံပါတ်",
            hint_text="09xxxxxxxxx",
            keyboard_type=ft.KeyboardType.PHONE,
            autofocus=True
        )
        
        name_input = ft.TextField(
            label="အမည် (Signup လုပ်ရန်အတွက်သာ)",
            hint_text="အမည်ထည့်ပါ",
            visible=False
        )

        is_signup_mode = False
        mode_title = ft.Text("🔑 အကောင့်သို့ ဝင်ရောက်ရန်", size=18, weight=ft.FontWeight.BOLD)
        action_btn = ft.ElevatedButton("Login ဝင်မည်", bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE, width=280, height=45)
        toggle_link = ft.TextButton("အကောင့်မရှိသေးပါက Signup လုပ်ရန် နှိပ်ပါ")

        def toggle_mode(e):
            nonlocal is_signup_mode
            is_signup_mode = not is_signup_mode
            if is_signup_mode:
                mode_title.value = "📝 အကောင့်သစ် ဖွင့်ရန်"
                name_input.visible = True
                action_btn.text = "Account ဖွင့်မည်"
                action_btn.bgcolor = ft.Colors.GREEN_600
                toggle_link.text = "အကောင့်ရှိပြီးသားဆိုပါက Login သို့ ပြန်သွားရန်"
            else:
                mode_title.value = "🔑 အကောင့်သို့ ဝင်ရောက်ရန်"
                name_input.visible = False
                action_btn.text = "Login ဝင်မည်"
                action_btn.bgcolor = ft.Colors.BLUE_600
                toggle_link.text = "အကောင့်မရှိသေးပါက Signup လုပ်ရန် နှိပ်ပါ"
            page.update()

        def handle_auth(e):
            phone = phone_input.value.strip() if phone_input.value else ""
            name = name_input.value.strip() if name_input.value else ""

            if not phone or len(phone) < 8:
                page.open(ft.SnackBar(ft.Text("🛑 ဖုန်းနံပါတ် မှန်ကန်စွာ ရိုက်ထည့်ပါ!"), bgcolor=ft.Colors.RED_800))
                return

            try:
                if is_signup_mode:
                    if not name:
                        page.open(ft.SnackBar(ft.Text("🛑 အမည် ရိုက်ထည့်ပါ!"), bgcolor=ft.Colors.RED_800))
                        return
                    
                    check_u = supabase.table("users").select("*").eq("id", phone).execute()
                    if check_u.data:
                        page.open(ft.SnackBar(ft.Text("🛑 ဒီဖုန်းနံပါတ်ဖြင့် အကောင့်ပွင့်ပြီးသား ဖြစ်ပါသည်။ Login ဝင်ပေးပါ။"), bgcolor=ft.Colors.RED_800))
                        return
                    
                    supabase.table("users").insert({"id": phone, "name": name, "balance": 0}).execute()
                    current_user["phone"] = phone
                    current_user["name"] = name
                else:
                    res = supabase.table("users").select("*").eq("id", phone).execute()
                    if not res.data:
                        page.open(ft.SnackBar(ft.Text("🛑 အကောင့် မရှိသေးပါ။ ကျေးဇူးပြု၍ Signup လုပ်ပေးပါ။"), bgcolor=ft.Colors.RED_800))
                        return
                    
                    current_user["phone"] = phone
                    current_user["name"] = res.data[0]["name"]

                refresh_wallet_ui()
                page.views.append(get_main_home_view())
                page.update()

            except Exception as ex:
                page.open(ft.SnackBar(ft.Text(f"Connection Error: {ex}"), bgcolor=ft.Colors.RED_800))

        action_btn.on_click = handle_auth
        toggle_link.on_click = toggle_mode

        return ft.View(
            route="/auth",
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CASINO, size=60, color=ft.Colors.AMBER_400),
                        mode_title,
                        ft.Container(height=10),
                        phone_input,
                        name_input,
                        ft.Container(height=10),
                        action_btn,
                        toggle_link
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    alignment=ft.alignment.center,
                    expand=True,
                    padding=20
                )
            ]
        )

    # ----------------------------------------------------
    # 👑 ADMIN SETTLE DIALOG (ထွက်ဂဏန်းထည့်၍ လျော်ရန်)
    # ----------------------------------------------------
    def open_settle_dialog(e):
        win_num_input = ft.TextField(label="ထွက်ဂဏန်း (ဥပမာ - 00)", keyboard_type=ft.KeyboardType.NUMBER, max_length=2)
        session_dropdown = ft.Dropdown(
            label="ပွဲချိန် ရွေးပါ",
            options=[ft.dropdown.Option("12:01 PM"), ft.dropdown.Option("04:30 PM")],
            value="12:01 PM"
        )

        def confirm_settle(e):
            w_num = win_num_input.value.strip() if win_num_input.value else ""
            s_val = session_dropdown.value
            if len(w_num) != 2:
                page.open(ft.SnackBar(ft.Text("🛑 ၂ လုံးဂဏန်း အတိအကျ ထည့်ပါ (ဥပမာ 05)"), bgcolor=ft.Colors.RED_800))
                return

            try:
                bets_res = supabase.table("bets").select("*").eq("session", s_val).eq("settled", False).execute()
                bets = bets_res.data if bets_res.data else []

                for bet in bets:
                    b_id = bet["id"]
                    u_id = bet["user_id"]
                    numbers_list = [n.strip() for n in bet["numbers"].split(",")]
                    unit_price = bet["unit_price"]

                    if w_num in numbers_list:
                        won_amount = unit_price * 80
                        u_res = supabase.table("users").select("balance").eq("id", u_id).execute()
                        if u_res.data:
                            cur_bal = u_res.data[0]["balance"]
                            supabase.table("users").update({"balance": cur_bal + won_amount}).eq("id", u_id).execute()

                    supabase.table("bets").update({"settled": True, "win_num": w_num}).eq("id", b_id).execute()

                page.close(settle_dialog)
                page.open(ft.SnackBar(ft.Text(f"✅ ပေါက်ဂဏန်း ({w_num}) ဖြင့် လျော်ပေးမှု ပြီးစီးပါပြီ!"), bgcolor=ft.Colors.GREEN_800))
            except Exception as ex:
                page.open(ft.SnackBar(ft.Text(f"Settle Error: {ex}"), bgcolor=ft.Colors.RED_800))

        settle_dialog = ft.AlertDialog(
            title=ft.Text("🏆 2D ပေါက်ဂဏန်း ထည့်သွင်းရန်", weight=ft.FontWeight.BOLD),
            content=ft.Column([session_dropdown, win_num_input], tight=True, spacing=10),
            actions=[
                ft.TextButton("မလုပ်တော့ပါ", on_click=lambda _: page.close(settle_dialog)),
                ft.ElevatedButton("လျော်မည် (Settle)", bgcolor=ft.Colors.AMBER_700, color=ft.Colors.WHITE, on_click=confirm_settle)
            ]
        )
        page.open(settle_dialog)

    # ----------------------------------------------------
    # 👑 ADMIN PANEL (ငွေသွင်း/ငွေထုတ် စီမံရန်)
    # ----------------------------------------------------
    def get_admin_panel_page():
        tx_list = ft.ListView(expand=True, spacing=10)

        def load_pending_transactions():
            tx_list.controls.clear()
            try:
                res = supabase.table("transactions").select("*").eq("status", "Pending").order("id", desc=True).execute()
                pending_txs = res.data if res.data else []
            except Exception as ex:
                pending_txs = []

            if not pending_txs:
                tx_list.controls.append(
                    ft.Container(
                        content=ft.Text("စောင့်ဆိုင်းဆဲ ငွေသွင်း/ငွေထုတ် တောင်းဆိုချက် မရှိပါ။", color=ft.Colors.GREY_400, size=13),
                        alignment=ft.alignment.center,
                        padding=20
                    )
                )
            else:
                for tx in pending_txs:
                    tx_id = tx["id"]
                    u_id = tx["user_id"]
                    tx_type = tx["type"]
                    amt = tx["amount"]
                    p_type = tx["pay_type"]
                    ref = tx["trans_id_or_acc"]

                    def approve_tx(e, tid=tx_id, uid=u_id, ttype=tx_type, tamt=amt):
                        try:
                            if ttype == "deposit":
                                u_res = supabase.table("users").select("balance").eq("id", uid).execute()
                                if u_res.data:
                                    c_bal = u_res.data[0]["balance"]
                                    supabase.table("users").update({"balance": c_bal + tamt}).eq("id", uid).execute()
                            
                            supabase.table("transactions").update({"status": "Approved"}).eq("id", tid).execute()
                            page.open(ft.SnackBar(ft.Text("✅ တောင်းဆိုချက်ကို အတည်ပြုလိုက်ပါပြီ။"), bgcolor=ft.Colors.GREEN_800))
                            refresh_wallet_ui()
                            load_pending_transactions()
                        except Exception as ex:
                            page.open(ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor=ft.Colors.RED_800))

                    def reject_tx(e, tid=tx_id, uid=u_id, ttype=tx_type, tamt=amt):
                        try:
                            if ttype == "withdraw":
                                u_res = supabase.table("users").select("balance").eq("id", uid).execute()
                                if u_res.data:
                                    c_bal = u_res.data[0]["balance"]
                                    supabase.table("users").update({"balance": c_bal + tamt}).eq("id", uid).execute()

                            supabase.table("transactions").update({"status": "Rejected"}).eq("id", tid).execute()
                            page.open(ft.SnackBar(ft.Text("❌ တောင်းဆိုချက်ကို ငြင်းပယ်လိုက်ပါပြီ။"), bgcolor=ft.Colors.RED_800))
                            refresh_wallet_ui()
                            load_pending_transactions()
                        except Exception as ex:
                            page.open(ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor=ft.Colors.RED_800))

                    title_str = "📥 ငွေသွင်းရန်" if tx_type == "deposit" else "📤 ငွေထုတ်ရန်"
                    color_str = ft.Colors.GREEN_400 if tx_type == "deposit" else ft.Colors.RED_400

                    card = ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"{title_str} ({p_type})", size=13, weight=ft.FontWeight.BOLD, color=color_str),
                                ft.Text(f"{amt:,} Ks", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(f"• User ဖုန်း: {u_id}", size=12),
                            ft.Text(f"• Ref / ဖုန်း: {ref}", size=12, color=ft.Colors.CYAN_300),
                            ft.Row([
                                ft.ElevatedButton("Approve", bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE, height=35, on_click=approve_tx),
                                ft.ElevatedButton("Reject", bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, height=35, on_click=reject_tx)
                            ], alignment=ft.MainAxisAlignment.END, spacing=10)
                        ], spacing=5),
                        padding=12,
                        bgcolor=ft.Colors.WHITE10,
                        border_radius=8
                    )
                    tx_list.controls.append(card)
            page.update()

        load_pending_transactions()

        return ft.View(
            route="/admin_panel",
            controls=[
                ft.AppBar(
                    title=ft.Text("👑 Admin Management Panel", size=18, weight=ft.FontWeight.BOLD),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_back)
                ),
                ft.Container(content=tx_list, padding=10, expand=True)
            ]
        )

    def verify_admin_pin(e):
        pin_input = ft.TextField(
            label="Admin PIN နံပါတ်",
            password=True,
            can_reveal_password=True,
            keyboard_type=ft.KeyboardType.NUMBER,
            max_length=6,
            autofocus=True
        )

        def check_pin(e):
            if pin_input.value == ADMIN_PIN:
                page.close(pin_dialog)
                page.views.append(get_admin_panel_page())
                page.update()
            else:
                page.open(ft.SnackBar(ft.Text("🛑 Admin PIN နံပါတ် မှားယွင်းနေပါသည်။"), bgcolor=ft.Colors.RED_800))

        pin_dialog = ft.AlertDialog(
            title=ft.Text("🔒 Admin Login", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text("Admin Management Panel သို့ ဝင်ရန် PIN နံပါတ် ရိုက်ထည့်ပါ။", size=12, color=ft.Colors.GREY_400),
                pin_input
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("မလုပ်တော့ပါ", on_click=lambda _: page.close(pin_dialog)),
                ft.ElevatedButton("ဝင်မည်", bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE, on_click=check_pin)
            ]
        )

        page.open(pin_dialog)

    # ----------------------------------------------------
    # 📜 HISTORY PAGE (ထိုးထားသော စာရင်းများ + Settle ခလုတ်)
    # ----------------------------------------------------
    def get_history_page():
        history_list = ft.ListView(expand=True, spacing=10)

        try:
            res = supabase.table("bets").select("*").eq("user_id", current_user["phone"]).order("id", desc=True).execute()
            bet_history = res.data if res.data else []
        except Exception as ex:
            bet_history = []

        if not bet_history:
            history_list.controls.append(
                ft.Container(
                    content=ft.Text("ထိုးထားသော စာရင်း မရှိသေးပါ", color=ft.Colors.GREY_400, size=14),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
        else:
            for item in bet_history:
                is_settled = item.get("settled", False)
                win_num = item.get("win_num", None)
                
                status_text = "⏳ စောင့်ဆိုင်းဆဲ"
                status_color = ft.Colors.AMBER_400

                if is_settled:
                    num_list = [n.strip() for n in item["numbers"].split(",")]
                    if win_num and win_num in num_list:
                        won_amt = item["unit_price"] * 80
                        status_text = f"🎉 ပေါက်ပါသည် (+{won_amt:,} Ks)"
                        status_color = ft.Colors.GREEN_400
                    else:
                        status_text = f"❌ မပေါက်ပါ (ထွက်: {win_num})"
                        status_color = ft.Colors.RED_400

                card = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"📅 {item['bet_date']} ({item['session']})", size=12, color=ft.Colors.CYAN_300, weight=ft.FontWeight.BOLD),
                            ft.Text(status_text, size=12, weight=ft.FontWeight.BOLD, color=status_color)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Divider(height=1, color=ft.Colors.WHITE10),
                        ft.Text(f"ဂဏန်းများ: {item['numbers']}", size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Text(f"အကွက်ရေ: {item['count']} ကွက်", size=11, color=ft.Colors.WHITE70),
                            ft.Text(f"စုစုပေါင်း: {item['total_cost']:,} Ks", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ], spacing=5),
                    padding=12,
                    bgcolor=ft.Colors.WHITE10,
                    border_radius=10
                )
                history_list.controls.append(card)

        return ft.View(
            route="/history",
            controls=[
                ft.AppBar(
                    title=ft.Text("ထိုးထားသော စာရင်းများ", size=18, weight=ft.FontWeight.BOLD),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_back),
                    actions=[
                        ft.IconButton(
                            icon=ft.Icons.MILITARY_TECH, 
                            tooltip="ပေါက်ဂဏန်းထည့်၍ လျော်ရန်", 
                            on_click=open_settle_dialog
                        )
                    ]
                ),
                ft.Container(content=history_list, padding=10, expand=True)
            ]
        )

    # ----------------------------------------------------
    # 💳 WALLET PAGE
    # ----------------------------------------------------
    def get_wallet_page():
        pay_info = {
            "KBZPay": {"number": "09984960264", "name": "U Thet Naing Soe"},
            "Wave Money": {"number": "09984960264", "name": "Myint Myint Than"}
        }

        pay_number_text = ft.Text(f"💳 KPay: {pay_info['KBZPay']['number']}", weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)
        pay_name_text = ft.Text(f"အမည်: {pay_info['KBZPay']['name']}", size=12)

        def on_pay_type_change(e):
            selected = pay_type.value
            if selected in pay_info:
                pay_number_text.value = f"💳 {selected}: {pay_info[selected]['number']}"
                pay_name_text.value = f"အမည်: {pay_info[selected]['name']}"
                page.update()

        pay_type = ft.Dropdown(
            label="ငွေလွှဲအမျိုးအစား ရွေးပါ",
            options=[
                ft.dropdown.Option("KBZPay"),
                ft.dropdown.Option("Wave Money"),
            ],
            value="KBZPay",
            width=300,
            on_change=on_pay_type_change
        )

        deposit_amt = ft.TextField(label="သွင်းမည့် ပမာဏ (ကျပ်)", keyboard_type=ft.KeyboardType.NUMBER, width=300)
        trans_id = ft.TextField(label="လုပ်ငန်းစဉ်နံပါတ် (နောက်ဆုံး ၆ လုံး)", keyboard_type=ft.KeyboardType.NUMBER, width=300)

        withdraw_amt = ft.TextField(label="ထုတ်မည့် ပမာဏ (ကျပ်)", keyboard_type=ft.KeyboardType.NUMBER, width=300)
        withdraw_acc = ft.TextField(label="လက်ခံမည့် KPay/Wave ဖုန်းနံပါတ်", keyboard_type=ft.KeyboardType.PHONE, width=300)

        def submit_deposit(e):
            amt_str = deposit_amt.value.strip() if deposit_amt.value else ""
            tid = trans_id.value.strip() if trans_id.value else ""

            if not amt_str or not amt_str.isdigit() or not tid:
                page.open(ft.SnackBar(ft.Text("🛑 ပမာဏနှင့် လုပ်ငန်းစဉ်နံပါတ် မှန်ကန်စွာ ဖြည့်ပေးပါ!"), bgcolor=ft.Colors.RED_800))
                return
            
            d_amt = int(amt_str)
            if d_amt <= 0:
                page.open(ft.SnackBar(ft.Text("🛑 ပမာဏ မှားယွင်းနေပါသည်။"), bgcolor=ft.Colors.RED_800))
                return

            try:
                supabase.table("transactions").insert({
                    "user_id": current_user["phone"],
                    "type": "deposit",
                    "amount": d_amt,
                    "pay_type": pay_type.value,
                    "trans_id_or_acc": tid,
                    "status": "Pending"
                }).execute()

                page.open(ft.SnackBar(ft.Text("✅ ငွေသွင်းတောင်းဆိုချက် ပေးပို့ပြီးပါပြီ။"), bgcolor=ft.Colors.GREEN_800))
                deposit_amt.value = ""
                trans_id.value = ""
                page.update()
            except Exception as ex:
                page.open(ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor=ft.Colors.RED_800))

        def submit_withdraw(e):
            amt_str = withdraw_amt.value.strip() if withdraw_amt.value else ""
            acc = withdraw_acc.value.strip() if withdraw_acc.value else ""

            if not amt_str or not amt_str.isdigit() or not acc:
                page.open(ft.SnackBar(ft.Text("🛑 ပမာဏနှင့် ဖုန်းနံပါတ် မှန်ကန်စွာ ဖြည့်ပေးပါ!"), bgcolor=ft.Colors.RED_800))
                return
            
            w_amt = int(amt_str)
            curr_bal = int(get_user_balance())

            if w_amt <= 0:
                page.open(ft.SnackBar(ft.Text("🛑 ပမာဏ မှားယွင်းနေပါသည်။"), bgcolor=ft.Colors.RED_800))
                return

            if w_amt > curr_bal:
                page.open(ft.SnackBar(ft.Text(f"🛑 ထုတ်ယူမည့် ပမာဏ ({w_amt:,} Ks) သည် လက်ကျန်ငွေ ({curr_bal:,} Ks) ထက် များနေပါသည်။"), bgcolor=ft.Colors.RED_800))
                return

            try:
                new_bal = curr_bal - w_amt
                supabase.table("users").update({"balance": new_bal}).eq("id", current_user["phone"]).execute()

                supabase.table("transactions").insert({
                    "user_id": current_user["phone"],
                    "type": "withdraw",
                    "amount": w_amt,
                    "pay_type": pay_type.value,
                    "trans_id_or_acc": acc,
                    "status": "Pending"
                }).execute()

                refresh_wallet_ui()
                page.open(ft.SnackBar(ft.Text("✅ ငွေထုတ်တောင်းဆိုချက် ပေးပို့ပြီးပါပြီ။"), bgcolor=ft.Colors.GREEN_800))
                withdraw_amt.value = ""
                withdraw_acc.value = ""
                page.update()
            except Exception as ex:
                page.open(ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor=ft.Colors.RED_800))

        def show_history(e):
            history_list = ft.ListView(expand=True, spacing=10, height=350)
            try:
                res = supabase.table("transactions").select("*").eq("user_id", current_user["phone"]).order("id", desc=True).execute()
                tx_history = res.data if res.data else []
            except Exception as ex:
                tx_history = []

            if not tx_history:
                history_list.controls.append(
                    ft.Container(content=ft.Text("မှတ်တမ်း မရှိသေးပါ", color=ft.Colors.GREY_400, size=13), alignment=ft.alignment.center, padding=20)
                )
            else:
                for tx in tx_history:
                    tx_type = "📥 ငွေသွင်း" if tx["type"] == "deposit" else "📤 ငွေထုတ်"
                    tx_color = ft.Colors.GREEN_400 if tx["type"] == "deposit" else ft.Colors.RED_400
                    
                    st = tx.get("status", "Pending")
                    st_text = "✅ အောင်မြင်" if st == "Approved" else ("❌ ငြင်းပယ်ပါသည်" if st == "Rejected" else "⏳ စောင့်ဆိုင်းဆဲ")
                    st_color = ft.Colors.GREEN_400 if st == "Approved" else (ft.Colors.RED_400 if st == "Rejected" else ft.Colors.AMBER_400)

                    card = ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"{tx_type} ({tx['pay_type']})", size=13, weight=ft.FontWeight.BOLD, color=tx_color),
                                ft.Text(st_text, size=11, color=st_color, weight=ft.FontWeight.BOLD)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Row([
                                ft.Text(f"ပမာဏ: {tx['amount']:,} Ks", size=12, weight=ft.FontWeight.BOLD),
                                ft.Text(f"Ref: {tx['trans_id_or_acc']}", size=11, color=ft.Colors.GREY_400)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ], spacing=4),
                        padding=10, bgcolor=ft.Colors.WHITE10, border_radius=8
                    )
                    history_list.controls.append(card)

            history_dialog = ft.AlertDialog(
                title=ft.Text("📜 ငွေသွင်း / ငွေထုတ် စာရင်းများ", weight=ft.FontWeight.BOLD, size=16),
                content=history_list,
                actions=[ft.TextButton("ပိတ်မည်", on_click=lambda _: page.close(history_dialog))]
            )
            page.open(history_dialog)

        deposit_view = ft.Column([
            ft.Text("📌 အောက်ပါ အကောင့်သို့ ငွေလွှဲပြီးပါက အချက်အလက် တင်ပေးပါ", size=12, color=ft.Colors.AMBER_300),
            ft.Container(content=ft.Column([pay_number_text, pay_name_text]), bgcolor=ft.Colors.WHITE10, padding=10, border_radius=8, width=300),
            pay_type, deposit_amt, trans_id,
            ft.ElevatedButton("ငွေသွင်းလွှာ တင်မည်", bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE, on_click=submit_deposit)
        ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        withdraw_view = ft.Column([
            pay_type, withdraw_amt, withdraw_acc,
            ft.ElevatedButton("ငွေထုတ်ရန် တောင်းဆိုမည်", bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE, on_click=submit_withdraw)
        ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        main_container = ft.Container(content=deposit_view, padding=10, alignment=ft.alignment.top_center)

        btn_deposit_tab = ft.ElevatedButton("ငွေသွင်းရန်", bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE, width=130)
        btn_withdraw_tab = ft.ElevatedButton("ငွေထုတ်ရန်", bgcolor=ft.Colors.WHITE10, color=ft.Colors.WHITE, width=130)

        def switch_to_deposit(e):
            btn_deposit_tab.bgcolor = ft.Colors.GREEN_700
            btn_withdraw_tab.bgcolor = ft.Colors.WHITE10
            main_container.content = deposit_view
            page.update()

        def switch_to_withdraw(e):
            btn_deposit_tab.bgcolor = ft.Colors.WHITE10
            btn_withdraw_tab.bgcolor = ft.Colors.RED_700
            main_container.content = withdraw_view
            page.update()

        btn_deposit_tab.on_click = switch_to_deposit
        btn_withdraw_tab.on_click = switch_to_withdraw

        toggle_row = ft.Row([btn_deposit_tab, btn_withdraw_tab], alignment=ft.MainAxisAlignment.CENTER, spacing=15)

        return ft.View(
            route="/wallet",
            controls=[
                ft.AppBar(
                    title=ft.Text("ငွေသွင်း / ငွေထုတ်", size=18, weight=ft.FontWeight.BOLD),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_back),
                    actions=[
                        ft.IconButton(icon=ft.Icons.HISTORY, tooltip="ငွေသွင်းငွေထုတ် စာရင်း", on_click=show_history)
                    ]
                ),
                ft.Container(height=10),
                toggle_row,
                ft.Divider(color=ft.Colors.WHITE10),
                main_container
            ]
        )

    # ----------------------------------------------------
    # 🎯 2D PAGE UI BUILDER (Date & TextField Updated)
    # ----------------------------------------------------
    def get_2d_page():
        now = datetime.now()
        current_time_val = now.time()

        t_12pm = datetime.strptime("12:00:00", "%H:%M:%S").time()
        t_430pm = datetime.strptime("16:30:00", "%H:%M:%S").time()

        target_date = now.date()

        if current_time_val >= t_430pm:
            target_date = now.date() + timedelta(days=1)
            disable_12pm = False
            disable_4pm = False
            default_session = "12:01 PM"
        else:
            disable_12pm = current_time_val >= t_12pm
            disable_4pm = False
            default_session = "04:30 PM" if disable_12pm else "12:01 PM"

        if target_date.weekday() in [5, 6]:
            return ft.View(
                route="/page_1",
                controls=[
                    ft.AppBar(
                        title=ft.Text("2D ထိုးမည့် စာမျက်နှာ", size=18, weight=ft.FontWeight.BOLD),
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_back)
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.EVENT_BUSY, size=70, color=ft.Colors.RED_400),
                            ft.Text("⚠️ စနေ/တနင်္ဂနွေ ပိတ်ရက်ဖြစ်ပါသည်!", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400),
                        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        expand=True, alignment=ft.alignment.center
                    )
                ]
            )

        # 💡 ထိုးမည့် ရက်စွဲနှင့် နေ့ (ဥပမာ - 23.07.2026 (Thursday))
        date_str_formatted = target_date.strftime("%d.%m.%Y")
        day_str_formatted = target_date.strftime("%A")
        date_display_text = ft.Text(
            f"📅 ထိုးမည့်ရက်စွဲ: {date_str_formatted} ({day_str_formatted})",
            size=13,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.CYAN_300
        )

        radio_12pm = ft.Radio(value="12:01 PM", label="12:01 PM (မနက်)", disabled=disable_12pm)
        radio_4pm = ft.Radio(value="04:30 PM", label="04:30 PM (ညနေ)", disabled=disable_4pm)

        session_radio = ft.RadioGroup(
            content=ft.Row([radio_12pm, radio_4pm], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            value=default_session
        )

        # 💡 ထိုးကြေး TextField (Box ထဲတွင် လှပစွာ ဝင်စေရန် label သုံးထားသည်)
        amount_input = ft.TextField(
            label="ထိုးကြေး (ကျပ်)",
            hint_text="100",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=115,
            height=45,
            text_size=13,
            label_style=ft.TextStyle(size=12)
        )

        def update_grid_ui():
            for btn in grid_buttons:
                num = btn.data
                if num in selected_numbers:
                    btn.bgcolor = ft.Colors.AMBER_600
                    btn.content.color = ft.Colors.BLACK
                else:
                    btn.bgcolor = ft.Colors.BLUE_GREY_900
                    btn.content.color = ft.Colors.WHITE
            page.update()

        def toggle_number(e, num_str):
            if num_str in selected_numbers:
                selected_numbers.remove(num_str)
            else:
                selected_numbers.append(num_str)
            update_grid_ui()

        def apply_quick_select(category, digit=None):
            selected_numbers.clear()
            
            if category == "စုံစုံ":
                for i in range(100):
                    num = f"{i:02d}"
                    if int(num[0]) % 2 == 0 and int(num[1]) % 2 == 0:
                        selected_numbers.append(num)
            elif category == "မမ":
                for i in range(100):
                    num = f"{i:02d}"
                    if int(num[0]) % 2 != 0 and int(num[1]) % 2 != 0:
                        selected_numbers.append(num)
            elif category == "အပူး":
                for i in range(10):
                    selected_numbers.append(f"{i}{i}")
            elif category == "ပါဝါ":
                selected_numbers.extend(["05", "50", "16", "61", "27", "72", "38", "83", "49", "94"])
            elif category == "နက္ခတ်":
                selected_numbers.extend(["07", "70", "18", "81", "24", "42", "35", "53", "69", "96"])
            elif category == "ပတ်သီး" and digit is not None:
                for i in range(100):
                    num = f"{i:02d}"
                    if digit in num:
                        selected_numbers.append(num)

            page.close(quick_select_dialog)
            update_grid_ui()

        patthit_input = ft.TextField(label="ပတ်သီး (0-9)", keyboard_type=ft.KeyboardType.NUMBER, max_length=1, width=150)

        def on_patthit_click(e):
            d = patthit_input.value.strip() if patthit_input.value else ""
            if not d.isdigit():
                page.open(ft.SnackBar(ft.Text("🛑 0 နှင့် 9 ကြား ဂဏန်းတစ်ခု ထည့်ပါ"), bgcolor=ft.Colors.RED_800))
                return
            apply_quick_select("ပတ်သီး", digit=d)

        quick_select_dialog = ft.AlertDialog(
            title=ft.Text("⚡ အမြန်ရွေးမည် / ပတ်သီး", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Row([
                    ft.ElevatedButton("စုံစုံ", on_click=lambda _: apply_quick_select("စုံစုံ")),
                    ft.ElevatedButton("မမ", on_click=lambda _: apply_quick_select("မမ")),
                    ft.ElevatedButton("အပူး", on_click=lambda _: apply_quick_select("အပူး")),
                ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ft.Row([
                    ft.ElevatedButton("ပါဝါ", on_click=lambda _: apply_quick_select("ပါဝါ")),
                    ft.ElevatedButton("နက္ခတ်", on_click=lambda _: apply_quick_select("နက္ခတ်")),
                ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ft.Divider(),
                ft.Row([patthit_input, ft.ElevatedButton("ပတ်သီးယူ", bgcolor=ft.Colors.AMBER_700, color=ft.Colors.WHITE, on_click=on_patthit_click)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], tight=True, spacing=10),
            actions=[ft.TextButton("ပိတ်မည်", on_click=lambda _: page.close(quick_select_dialog))]
        )

        btn_quick_select = ft.OutlinedButton(
            text="အမြန်ရွေး",
            icon=ft.Icons.FLASH_ON,
            style=ft.ButtonStyle(color=ft.Colors.AMBER_400),
            on_click=lambda _: page.open(quick_select_dialog)
        )

        grid_buttons = []
        for i in range(100):
            num_str = f"{i:02d}"
            btn = ft.Container(
                content=ft.Text(num_str, weight=ft.FontWeight.BOLD, size=13, color=ft.Colors.WHITE),
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.BLUE_GREY_900,
                border_radius=8,
                data=num_str,
                on_click=lambda e, n=num_str: toggle_number(e, n)
            )
            grid_buttons.append(btn)

        number_grid = ft.GridView(
            controls=grid_buttons,
            runs_count=5,
            max_extent=60,
            spacing=8,
            run_spacing=8,
            expand=True,
        )

        def process_final_bet(unit_price, total_cost, target_session, confirm_dialog):
            page.close(confirm_dialog)

            curr_bal = get_user_balance()
            new_bal = curr_bal - total_cost
            formatted_date = target_date.strftime("%d.%m.%Y")

            try:
                supabase.table("users").update({"balance": new_bal}).eq("id", current_user["phone"]).execute()

                supabase.table("bets").insert({
                    "user_id": current_user["phone"],
                    "bet_date": formatted_date,
                    "session": target_session,
                    "numbers": ', '.join(sorted(selected_numbers)),
                    "count": len(selected_numbers),
                    "unit_price": unit_price,
                    "total_cost": total_cost,
                    "settled": False
                }).execute()

                refresh_wallet_ui()
                selected_numbers.clear()
                amount_input.value = ""
                update_grid_ui()

                page.open(
                    ft.SnackBar(
                        ft.Text(f"✅ ထိုးစာရင်း အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ!"),
                        bgcolor=ft.Colors.GREEN_800
                    )
                )

            except Exception as ex:
                page.open(ft.SnackBar(ft.Text(f"Bet Error: {ex}"), bgcolor=ft.Colors.RED_800))

        def submit_bet(e):
            val_str = amount_input.value
            target_session = session_radio.value

            if not selected_numbers:
                page.open(ft.SnackBar(ft.Text("ကျေးဇူးပြု၍ ဂဏန်းအနည်းဆုံး တစ်လုံး ရွေးပါ!")))
                return

            if not val_str or not val_str.isdigit():
                page.open(ft.SnackBar(ft.Text("ကျေးဇူးပြု၍ ထိုးကြေးပမာဏ မှန်ကန်စွာ ရိုက်ထည့်ပါ!")))
                return

            unit_price = int(val_str)
            if unit_price < 100:
                page.open(ft.SnackBar(ft.Text("🛑 အနည်းဆုံး ၁၀၀ ကျပ်မှစ၍ ထိုးရပါမည်။"), bgcolor=ft.Colors.RED_800))
                return

            total_cost = unit_price * len(selected_numbers)
            current_bal = get_user_balance()

            if total_cost > current_bal:
                page.open(ft.SnackBar(ft.Text(f"🛑 လက်ကျန်ငွေ မလုံလောက်ပါ။ (လိုအပ်ငွေ: {total_cost:,} Ks)"), bgcolor=ft.Colors.RED_800))
                return

            sorted_nums = ', '.join(sorted(selected_numbers))

            confirm_dialog = ft.AlertDialog(
                title=ft.Text("📌 ထိုးစာရင်း အတည်ပြုရန်", weight=ft.FontWeight.BOLD),
                content=ft.Column([
                    ft.Text(f"• ရက်စွဲ/ချိန်: {target_date.strftime('%d.%m.%Y')} ({target_session})", size=13, color=ft.Colors.CYAN_300),
                    ft.Text(f"• ဂဏန်းများ: {sorted_nums}", size=13, color=ft.Colors.AMBER_300),
                    ft.Text(f"• အကွက်ရေ: {len(selected_numbers)} ကွက်", size=13),
                    ft.Text(f"• စုစုပေါင်း: {total_cost:,} ကျပ်", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400),
                ], tight=True, spacing=8),
                actions=[
                    ft.TextButton("မဟုတ်ပါ", on_click=lambda _: page.close(confirm_dialog)),
                    ft.ElevatedButton(
                        "သေချာပြီ", 
                        bgcolor=ft.Colors.GREEN_600, 
                        color=ft.Colors.WHITE,
                        on_click=lambda _: process_final_bet(unit_price, total_cost, target_session, confirm_dialog)
                    ),
                ]
            )

            page.open(confirm_dialog)

        submit_btn = ft.ElevatedButton("ထိုးမည်", bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE, height=45, width=80)
        submit_btn.on_click = submit_bet

        return ft.View(
            route="/page_1",
            controls=[
                ft.AppBar(
                    title=ft.Text("2D ထိုးမည့် စာမျက်နှာ", size=18, weight=ft.FontWeight.BOLD),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_back),
                    actions=[
                        ft.IconButton(
                            icon=ft.Icons.RECEIPT_LONG, 
                            tooltip="ထိုးထားသော စာရင်းများ",
                            on_click=lambda _: (page.views.append(get_history_page()), page.update())
                        )
                    ]
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([date_display_text], alignment=ft.MainAxisAlignment.CENTER),
                        session_radio,
                        ft.Container(content=number_grid, expand=True),
                        ft.Row([amount_input, btn_quick_select, submit_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ]),
                    expand=True, padding=10
                )
            ]
        )

    # ----------------------------------------------------
    # 🏠 MAIN HOME VIEW
    # ----------------------------------------------------
    def get_main_home_view():
        user_wallet = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color=ft.Colors.GREEN_400, size=20),
                ft.Column([
                    ft.Text("လက်ကျန်ငွေ", size=10, color=ft.Colors.GREY_400),
                    wallet_text,
                ], spacing=1)
            ]),
            padding=10, bgcolor=ft.Colors.WHITE10, border_radius=10
        )

        user_info = ft.Container(
            content=ft.Row([
                ft.Column([user_name_text, user_phone_text], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=1),
                ft.Icon(ft.Icons.ACCOUNT_CIRCLE, color=ft.Colors.AMBER_400, size=28),
            ]),
            padding=10, bgcolor=ft.Colors.WHITE10, border_radius=10
        )

        header_section = ft.Row([user_wallet, user_info], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        banner_image = ft.Container(
        content=ft.Image(
            src="/Users/macbookpro/Downloads/20251222-011552.png",
            width=200,
            height=200,
            fit=ft.ImageFit.COVER,
        ),
        alignment=ft.alignment.center,
        width=300,
        margin=ft.margin.only(bottom=15)
        )

        btn_2d = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.CASINO, size=28),
                ft.Text("2D ထိုးမည်", size=20, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=12)),
            width=280, height=55,
            on_click=lambda _: (page.views.append(get_2d_page()), page.update())
        )

        btn_history = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.RECEIPT_LONG, size=28),
                ft.Text("ထိုးထားသော စာရင်းများ", size=18, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            style=ft.ButtonStyle(bgcolor=ft.Colors.AMBER_700, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=12)),
            width=280, height=55,
            on_click=lambda _: (page.views.append(get_history_page()), page.update())
        )

        btn_wallet = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.SWAP_HORIZ, size=28),
                ft.Text("ငွေသွင်း - ငွေထုတ်", size=18, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            style=ft.ButtonStyle(bgcolor=ft.Colors.TEAL_700, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=12)),
            width=280, height=55,
            on_click=lambda _: (page.views.append(get_wallet_page()), page.update())
        )

        return ft.View(
            route="/home",
            controls=[
                ft.AppBar(
                    title=ft.Text("Lucky 2D", color="Yellow", size=18, weight=ft.FontWeight.BOLD),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    automatically_imply_leading=False,
                    actions=[
                        ft.IconButton(
                            icon=ft.Icons.ADMIN_PANEL_SETTINGS, 
                            tooltip="Admin Management Panel",
                            on_click=verify_admin_pin
                        ),
                        ft.IconButton(
                            icon=ft.Icons.LOGOUT,
                            on_click=lambda _: (page.views.clear(), page.views.append(show_login_signup_view()), page.update())
                        )
                    ]
                ),
                ft.Column([
                    header_section,
                    ft.Container(
                        content=ft.Column([banner_image, btn_2d, btn_history, btn_wallet], 
                        spacing=15, 
                        alignment=ft.MainAxisAlignment.CENTER
                        ),
                        expand=True,
                        alignment=ft.alignment.center
                    )
                ], expand=True)
            ],
            padding=15
        )

    page.on_view_pop = lambda e: go_back()
    page.views.append(show_login_signup_view())
    page.update()

ft.app(target=main)