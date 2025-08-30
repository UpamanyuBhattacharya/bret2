# -------------------- Grid Rendering (FAST, no widgets) --------------------
n, cols = st.session_state.n, st.session_state.cols
rows = (n + cols - 1) // cols

def _cell_label(i: int) -> str:
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
        return "🟩" if i <= opened else "◻️"

# Build one HTML blob instead of 100 widgets
cells_html = []
cells_html.append("""
<style>
.bret-row { white-space: nowrap; }
.bret-cell {
  display:inline-block;
  width:64px;             /* adjust cell width */
  padding:8px 0;
  margin:2px;
  text-align:center;
  border:1px solid #e5e7eb;
  border-radius:8px;
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Emoji, Apple Color Emoji, Noto Color Emoji;
  user-select:none;
}
.bret-wrap { overflow-x:auto; }
</style>
<div class="bret-wrap">
""")

for r in range(rows):
    row_cells = []
    for c in range(cols):
        i = r * cols + c + 1
        if i > n:
            break
        row_cells.append(f'<span class="bret-cell">{_cell_label(i)} {i}</span>')
    cells_html.append(f'<div class="bret-row">{"".join(row_cells)}</div>')

cells_html.append("</div>")
st.markdown("".join(cells_html), unsafe_allow_html=True)

