
DARK={
    "bg":       "#0D0F14","bg2":"#141720","card":"#1A1E2E","hover":"#222840",
    "accent":   "#4F8EF7","accent2":"#6C63FF","green":"#2DD4A7","orange":"#F5A623",
    "red":      "#FF5F5F","purple":"#9B7CFF",
    "fg":       "#E8EAF6","fg2":"#8A92B2","fg3":"#525A7A",
    "border":   "#252A3D","sidebar":"#0A0C12","topbar":"#0D0F14",
    "prog_bg":  "#1A1E2E",
}
LIGHT={
    "bg":       "#F0F2F8","bg2":"#E8EBF5","card":"#FFFFFF","hover":"#EEF1FF",
    "accent":   "#3B6FE8","accent2":"#5750D4","green":"#1DAD8A","orange":"#E09420",
    "red":      "#E84A4A","purple":"#7C65E0",
    "fg":       "#1A1D30","fg2":"#4A5070","fg3":"#8890AF",
    "border":   "#D0D5ED","sidebar":"#E2E5F2","topbar":"#F0F2F8",
    "prog_bg":  "#E8EBF5",
}

NAV=[
    {"id":"dashboard", "label":"Dashboard",    "icon":"⬡"},
    {"id":"cleanup",   "label":"Cleanup",       "icon":"🧹"},
    {"id":"disk",      "label":"Disk Analyzer", "icon":"💿"},
    {"id":"startup",   "label":"Startup",       "icon":"⚡"},
    {"id":"registry",  "label":"Registry",      "icon":"🔧"},
    {"id":"network",   "label":"Network",       "icon":"🌐"},
    {"id":"gaming",    "label":"Gaming",        "icon":"🎮"},
    {"id":"monitoring","label":"Monitoring",    "icon":"📊"},
    {"id":"reports",   "label":"Reports",       "icon":"📋"},
    {"id":"restore",   "label":"Restore",       "icon":"↩"},
    {"id":"settings",  "label":"Settings",      "icon":"⚙"},
]
PAGE_TITLES={n["id"]:n["label"] for n in NAV}
