"""Gedeelde helpers voor sector-templates. Elk template blijft verantwoordelijk voor zijn eigen HTML/CSS."""

def esc(s):
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def build_hours_rows(hours, closed_class="hours-row"):
    rows = []
    for day, time in hours:
        closed = "closed" if "esloten" in time or "losed" in time else ""
        rows.append(f'<div class="{closed_class} {closed}"><span>{esc(day)}</span><span>{esc(time)}</span></div>')
    return "\n".join(rows)

def build_highlights(items, mark="—"):
    lis = [f'<li><span class="mark">{esc(mark)}</span>{esc(i)}</li>' for i in items]
    return "\n".join(lis)

def build_list(items, item_class=""):
    cls = f' class="{item_class}"' if item_class else ""
    lis = [f'<li{cls}>{esc(i)}</li>' for i in items]
    return "\n".join(lis)

def maps_query(address):
    return address.replace(" ", "+")
