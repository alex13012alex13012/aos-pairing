import streamlit as st
import json
import os

st.set_page_config(layout="wide")
st.title("AoS - Pairing - Aléa de la méta")

# =========================
# MODE (OBLIGATOIRE)
# =========================
mode = st.sidebar.radio("Mode", ["Préparation", "Tournoi"],index=1)
selected_round = st.sidebar.selectbox("Ronde", ["R1", "R2", "R3", "R4", "R5"])

# =========================
# CONFIG
# =========================
joueurs = [
    "Nicolas Vercruysse (Ekyeez)",
    "Alexandre Pujol (Alex Pjl)",
    "Julien Paccallet (Galhadar)",
    "Alexandre Bochet-Mérand (Acortex)",
    "Christophe Canalis (Iscariote)",
    "Louis Moulin (Groot)"
]

scenarios = ["S1", "S2", "S3"]

# =========================
# FILE SYSTEM
# =========================
def file_round(r):
    return f"{r}.json"

def load_round(r):
    if os.path.exists(file_round(r)):
        with open(file_round(r), "r") as f:
            return json.load(f)
    return {
        "adversaires": [],
        "players": {},
        "history": [],
        "score_own": "",
        "score_enemy": "",
        "result": ""
    }

def save_round(r, data):
    with open(file_round(r), "w") as f:
        json.dump(data, f, indent=2)

round_data = load_round(selected_round)

# =========================
# PLAYER INIT
# =========================
def get_player(j):
    if j not in round_data["players"]:
        round_data["players"][j] = {
            "good_scen": [],
            "ok_scen": [],
            "bad_scen": [],
            "good": [],
            "bad": [],
            "defensif": False
        }
    return round_data["players"][j]

# =========================
# SCORE FUNCTION
# =========================
def score(player, scen, adv):
    s = 0
    if scen in player.get("good_scen", []):
        s += 4
    elif scen in player.get("ok_scen", []):
        s += 2
    elif scen in player.get("bad_scen", []):
        s -= 4

    if adv in player.get("good", []):
        s += 3
    if adv in player.get("bad", []):
        s -= 3

    return s

# =========================
# ADV INPUT
# =========================
st.header(f"Ronde {selected_round}")

if mode == "Préparation":
    adv_text = st.text_area(
        "Armées adverses",
        value="\n".join(round_data.get("adversaires", []))
    )

    round_data["adversaires"] = [a.strip() for a in adv_text.split("\n") if a.strip()]

    # ============================================================
# 🟢 PREPARATION
# ============================================================
if mode == "Préparation":

    # 🆕 AJOUT IMAGES (NE TOUCHE PAS AU RESTE)
    st.subheader("🖼️ Images des scénarios")

    os.makedirs("images", exist_ok=True)

    for scen in scenarios:
        uploaded = st.file_uploader(
            f"{selected_round} - {scen}",
            type=["png", "jpg", "jpeg"],
            key=f"{selected_round}_{scen}_img"
        )

        if uploaded:
            with open(f"images/{selected_round}_{scen}.png", "wb") as f:
                f.write(uploaded.getbuffer())

            st.success(f"Image sauvegardée pour {scen}")

    # ===== TON CODE EXISTANT =====
    for j in joueurs:
        d = get_player(j)

        st.subheader(j)

        d["good_scen"] = st.multiselect(
            "Scénarios bons",
            scenarios,
            default=d["good_scen"],
            key=f"{selected_round}_{j}_gs"
        )

        d["ok_scen"] = st.multiselect(
            "Scénarios ok",
            scenarios,
            default=d["ok_scen"],
            key=f"{selected_round}_{j}_os"
        )

        d["bad_scen"] = st.multiselect(
            "Scénarios mauvais",
            scenarios,
            default=d["bad_scen"],
            key=f"{selected_round}_{j}_bs"
        )

        d["good"] = st.multiselect(
            "Matchups bons",
            round_data["adversaires"],
            default=d["good"],
            key=f"{selected_round}_{j}_gm"
        )

        d["bad"] = st.multiselect(
            "Matchups mauvais",
            round_data["adversaires"],
            default=d["bad"],
            key=f"{selected_round}_{j}_bm"
        )

        d["defensif"] = st.checkbox(
            "Défensif",
            value=d.get("defensif", False),
            key=f"{selected_round}_{j}_def"
        )

        round_data["players"][j] = d

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Sauvegarder"):
            save_round(selected_round, round_data)
            st.success("Sauvegardé")

    with col2:
        if st.button("🧹 Reset"):
            save_round(selected_round, {
                "adversaires": [],
                "players": {},
                "history": []
            })
            st.rerun()

# ============================================================
# 🎮 TOURNOI
# ============================================================
else:

    data = round_data["players"]
    history = round_data["history"]

    if st.button("🔄 Reset la ronde"):
        round_data["history"] = []
        save_round(selected_round, round_data)
        st.rerun()

    used_adv = set()
    for h in history:
        used_adv.add(h["atk_adv"])
        used_adv.add(h["def_adv"])

    available_adv = [a for a in round_data["adversaires"] if a not in used_adv]

    st.subheader("⚔️ Armées adverses restantes ⚔️")
    st.write(", ".join(available_adv) if available_adv else "Aucune armée restante")

    if len(history) >= 3:

        st.success("🏁 Ronde terminée")

        st.subheader("📊 Résumé des 3 parties")

        total_score_round = 0

        for h in history:
            atk = score(data[h["atk"]], h["scenario"], h["atk_adv"])
            deff = score(data[h["def"]], h["scenario"], h["def_adv"])
            total = atk + deff
            total_score_round += total

            st.write(
                f"{h['scenario']} | "
                f"{h['def']} vs {h['atk_adv']} | "
                f"{h['atk']} vs {h['def_adv']} | "
                f"Score : {total}"
            )

        st.success(f"🏆 Score total de la ronde (6 joueurs) : {total_score_round}")


        st.stop()









    scen_index = len(history) + 1
    scen = f"S{scen_index}"

    # =========================
    # AFFICHAGE DES 3 SCÉNARIOS
    # =========================
    cols = st.columns(3)

    for i, s in enumerate(scenarios):
        img_path = f"images/{selected_round}_{s}.png"

        is_active = (s == scen)

        with cols[i]:
            if is_active:
                st.markdown(
                    "<div style='border:3px solid red; border-radius:10px; padding:5px'>",
                    unsafe_allow_html=True
                )

            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            else:
                st.write(f"{s} - pas d'image")

            if is_active:
                st.markdown("</div>", unsafe_allow_html=True)


      
    
    used_players_global = set()
    for h in history:
        used_players_global.add(h["def"])
        used_players_global.add(h["atk"])

    used_def_this_scen = set(
        h["def"] for h in history if h["scenario"] == scen
    )

    available_players = [
        j for j in data.keys()
        if j not in used_players_global
        and j not in used_def_this_scen
    ]




    def scen_level(player, s):
        if s in player.get("good_scen", []):
            return 3
        elif s in player.get("ok_scen", []):
            return 2
        elif s in player.get("bad_scen", []):
            return -2
        return 0


    def def_score(j):

        player = data[j]

        if scen in player.get("good_scen", []):
            score = 3
            current_level = 3
        elif scen in player.get("ok_scen", []):
            score = 2
            current_level = 2
        elif scen in player.get("bad_scen", []):
            score = -2
            current_level = -2
        else:
            score = 0
            current_level = 0



        played_scenarios = {h["scenario"] for h in history}

        for fs in player.get("good_scen", []) + player.get("ok_scen", []):

            # scénario futur uniquement
            if fs not in played_scenarios:

                # si futur meilleur que actuel
                if scen_level(player, fs) > current_level:
                    score -= 1
                    break


        bad_matchups_count = 0
        for a in available_adv:
            if a in player.get("bad", []):
                bad_matchups_count += 1

        if bad_matchups_count >= 2:
            score -= 2

        if player.get("defensif", False):
            score += 1

        return score

    def_rank = sorted(
        [(def_score(j), j) for j in available_players],
        reverse=True
    )

    positive_def = [(s, j) for s, j in def_rank if s > 0]

    st.subheader("🛡️ Défenseurs conseillés")

    for s, j in positive_def:
        st.write(f"{j} ({s})")

    if len(positive_def) >= 2:
        top2_def = [j for _, j in positive_def[:2]]
        st.success(f"👉 Recommandation : {top2_def[0]} & {top2_def[1]}")
    elif len(positive_def) == 1:
        st.success(f"👉 Recommandation : {positive_def[0][1]}")
    else:
        st.warning("Aucun défenseur recommandé")

    defenseur = st.selectbox("Ton défenseur", available_players)

    adv_def = st.selectbox("Défenseur adverse", available_adv)

    adv_pool = st.multiselect(
        "Attaquants adverses (2)",
        available_adv,
        max_selections=2
    )

    adv_choice = None

    def adv_score(a):

        player_def = data.get(defenseur)

        if not player_def:
            return 0

        score = 0

        if a in player_def.get("good", []):
            score += 3
        elif a in player_def.get("bad", []):
            score -= 3

        return score

    if len(adv_pool) == 2:

        scored = [(a, adv_score(a)) for a in adv_pool]
        scored.sort(key=lambda x: x[1], reverse=True)

        st.write(f"{scored[0][0]} → {scored[0][1]}")
        st.write(f"{scored[1][0]} → {scored[1][1]}")

        st.success(f"👉 Meilleur choix : {scored[0][0]}")

        adv_choice = st.selectbox("Choix final attaquant adverse", adv_pool)

    atk_candidates = [
        j for j in available_players
        if j != defenseur
    ]

    def atk_score(j):

        player = data[j]

        scen_score = 0
        if scen in player.get("good_scen", []):
            scen_score = 3
        elif scen in player.get("ok_scen", []):
            scen_score = 2
        elif scen in player.get("bad_scen", []):
            scen_score = -2

        army_score = 0
        if adv_def in player.get("good", []):
            army_score = 3
        elif adv_def in player.get("bad", []):
            army_score = -3

        return scen_score + army_score

    atk_rank = sorted(
        [(atk_score(j), j) for j in atk_candidates],
        reverse=True
    )

    st.subheader("⚔️ Tes 2 meilleurs attaquants")

    for s, j in atk_rank[:3]:
        st.write(f"{j} ({s})")

    if len(atk_rank) >= 2:
        top2 = [j for _, j in atk_rank[:2]]
        st.success(f"👉 Recommandation : {top2[0]} & {top2[1]}")

    attaquant = st.selectbox("Ton attaquant", atk_candidates)

    if st.button("Valider scénario") and adv_choice:

        round_data["history"].append({
            "scenario": scen,
            "atk": attaquant,
            "def": defenseur,
            "atk_adv": adv_choice,
            "def_adv": adv_def
        })

        save_round(selected_round, round_data)
        st.rerun()

    st.subheader("Résumé")

    if history:
        for h in history:
            atk = score(data[h["atk"]], h["scenario"], h["atk_adv"])
            deff = score(data[h["def"]], h["scenario"], h["def_adv"])
            total = atk + deff

            st.write(
                f"{h['scenario']} | "
                f"{h['def']} vs {h['atk_adv']} | "
                f"{h['atk']} vs {h['def_adv']} | "
                f"Score : {total}"
            )
    else:
        st.write("Aucun scénario joué pour le moment")
