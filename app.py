import streamlit as st
import random
import time
from datetime import datetime

# -------------------- Page Setup --------------------
st.set_page_config(page_title="BRET — Bomb Risk Elicitation Task", page_icon="💣", layout="wide")
st.title("💣 Bomb Risk Elicitation Task (BRET)")
st.caption("Open boxes sequentially. Stop whenever you like. The bomb is revealed only after you stop.")

# -------------------- Defaults & Helpers --------------------
DEFAULT_N = 100
DEFAULT_COLS = 10
DEFAULT_PAYOFF_PER_BOX = 10  # change as needed (e.g., points, rupees, tokens)

def _reset_game(n_boxes: int):
    st.session_state.n = n_boxes
    st.session_state.cols = DEFAULT_COLS
    st.session_state.payoff_per_box = st.session_state.get("payoff_per_box", DEFAULT_PAYOFF_PER_BOX)

    st.session_state.bomb_idx = random.randint(1, n_boxes)  # hidden until reveal
    st.session_state.opened = 0  # number of sequential boxes opened (1..opened are open)
    st.session_state.revealed = False  # whether participant has stopped and bomb is shown
    st.session_state.payoff = None
    st.session_state.outcome = None  # "safe" or "bombed"
    st.session_state.run_id = datetime.now().strftime("%Y%m%d-%H%M%S")

def _compute_payoff():
    # If any opened box contains the bomb (i.e., bomb index <= opened), payoff is 0
    if st.session_state.bomb_idx <= st.session_state.opened:
        st.session_state.outcome = "bombed"
        st.session_state.payoff = 0
    else:
        st.session_state.outcome = "safe"
        st.session_state.payoff = st.session_state.opened * st.session_state.payoff_per_box

def _ensure_state():
    if "n" not in st.session_state:
        _reset_game(DEFAULT_N)

# -------------------- Initialize --------------------
_ensure_state()

# -------------------- Sidebar Controls --------------------
st.sidebar.header("Settings")
with st.sidebar:
    payoff_val = st.number_input("Payoff per safe box", min_value=1, value=st.session_state.payoff_per_box, step=1)
    if payoff_val != st.session_state.payoff_per_box:
        st.session_state.payoff_per_box = payoff_val

    n_val = st.number_input("Total boxes", min_value=10, max_value=200, value=st.session_state.n, step=10)
    cols_val = st.number_input("Grid columns", min_value=5, max_value=20, value=st.session_state.cols, step=1)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔁 New Participant / New Game"):
            _reset_game(int(n_val))
            st.session_state.cols = int(cols_val)
            st.rerun()
    with col2:
        st.write(f"Run ID: `{st.session_state.run_id}`")

# -------------------- Status Line --------------------
status = f"Boxes opened: **{st.session_state.opened} / {st.session_state.n}**"
if not st.session_state.revealed:
    st.subheader(status)
else:
    # Show outcome + payoff
    if st.session_state.outcome == "bombed":
        st.subheader(f"💥 Bomb was in box **{st.session_state.bomb_idx}** → **Payoff: 0**")
    else:
        st.subheader(
            f"✅ Safe! Bomb was in box **{st.session_state.bomb_idx}** → "
            f"**Payoff: {st.session_state.payoff}** "
            f"({st.session_state.opened} × {st.session_state.payoff_per_box})"
        )

# -------------------- Controls Row --------------------
c_open, c_stop, c_note = st.columns([1,1,3])
with c_open:
    disabled_open = st.session_state.revealed or (st.session_state.opened >= st.session_state.n)
    if st.button(
        f"📦 Open next box (#{st.session_state.opened + 1})",
        disabled=disabled_open,
        use_container_width=True
    ):
        st.session_state.opened += 1
        # no reveal yet; bomb remains hidden regardless of whether we already passed it

with c_stop:
    disabled_stop = st.session_state.revealed or (st.session_state.opened == 0)
    if st.button("🛑 Stop & Reveal", disabled=disabled_stop, use_container_width=True):
        _compute_payoff()
        st.session_state.revealed = True
        # brief pause for drama (optional; comment out if you dislike delays)
        time.sleep(0.3)
        st.rerun()

with c_note:
    st.markdown(
        """
        **Rules**  
        • You must open boxes **in order** (1, 2, 3, …).  
        • Click **Stop & Reveal** anytime to lock in your payoff.  
        • If the bomb is among the boxes you opened, your payoff is **0**.  
        • Otherwise, you earn: `opened_boxes × payoff_per_box`.
        """
    )

st.divider()

# -------------------- Grid Rendering --------------------
# We show a 10x10 (or C columns) grid. Only the **next** sequential box is clickable via the "Open next" button above,
# so all cell buttons are disabled. The grid is purely visual and shows:
# - 🟩 for opened safe boxes (before reveal)
# - 🟩 for opened safe boxes (after reveal, still safe)
# - 💣 for the bomb (only after reveal)
# - ◻️ for unopened
n, cols = st.session_state.n, st.session_state.cols
rows = (n + cols - 1) // cols

def _cell_label(i: int) -> str:
    # i is 1-based index
    opened = st.session_state.opened
    revealed = st.session_state.revealed
    bomb = st.session_state.bomb_idx

    if revealed:
        if i == bomb:
            return "💣"
        elif i <= opened and i != bomb:
            return "🟩"
        else:
            return "◻️"
    else:
        # Not revealed yet: never show the bomb; show opened as green
        if i <= opened:
            return "🟩"
        else:
            return "◻️"

for r in range(rows):
    cols_container = st.columns(cols, gap="small")
    for c in range(cols):
        i = r * cols + c + 1
        if i > n:
            continue
        with cols_container[c]:
            st.button(
                f"{_cell_label(i)} {i}",
                key=f"cell_{i}",
                use_container_width=True,
                disabled=True  # grid is display-only to enforce sequential clicking
            )

st.divider()

# -------------------- Trial Log (optional) --------------------
with st.expander("Session details / export", expanded=False):
    st.write(
        {
            "run_id": st.session_state.run_id,
            "n_boxes": st.session_state.n,
            "opened": st.session_state.opened,
            "bomb_index": st.session_state.bomb_idx if st.session_state.revealed else "(hidden until reveal)",
            "payoff_per_box": st.session_state.payoff_per_box,
            "outcome": st.session_state.outcome if st.session_state.revealed else "(not revealed)",
            "payoff": st.session_state.payoff if st.session_state.revealed else "(not revealed)",
        }
    )
    st.caption("Copy this dictionary for your records. Add your own logging to a database or CSV if running lab sessions.")

