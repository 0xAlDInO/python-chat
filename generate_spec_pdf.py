from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

def generate_pdf():
    pdf_filename = "SPEC_TECHNIQUE_FRONTOFFICE.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#3B82F6'),
        fontName='Helvetica-Bold',
        alignment=0,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        fontName='Helvetica-Oblique',
        spaceAfter=20
    )

    h2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1E293B'),
        fontName='Helvetica-Bold',
        spaceBefore=14,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )

    story = []

    # Title & Header
    story.append(Paragraph("OXMEMBER — Spécification Technique Front-Office", title_style))
    story.append(Paragraph("Document d'architecture et de fonctionnalités de l'interface utilisateur pour les collaborateurs Oxalix", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3B82F6'), spaceAfter=15))

    # 1. Introduction & Authentication
    story.append(Paragraph("1. Authentification & Données Back-Office", h2_style))
    story.append(Paragraph(
        "L'accès au Front-Office d'OXMEMBER s'effectue via un identifiant unique attribué par le Back-Office (ex: <b>OX-001</b>, <b>OX-002</b>). "
        "À partir de cet ID, l'application résout automatiquement dans la base de données centrale les informations officielles de l'employé : "
        "son prénom, son nom de famille ainsi que sa fonction exacte au sein de l'entreprise Oxalix.",
        body_style
    ))

    # Table of Users
    table_data = [
        [Paragraph("<b>ID Utilisateur</b>", body_style), Paragraph("<b>Nom & Prénom</b>", body_style), Paragraph("<b>Fonction Officielle</b>", body_style)],
        [Paragraph("OX-001", body_style), Paragraph("Alice Dupont", body_style), Paragraph("Chef de Projet", body_style)],
        [Paragraph("OX-002", body_style), Paragraph("Jean Martin", body_style), Paragraph("Développeur Senior", body_style)],
        [Paragraph("OX-003", body_style), Paragraph("Sophie Bernard", body_style), Paragraph("UI/UX Designer", body_style)],
        [Paragraph("OX-004", body_style), Paragraph("Thomas Dubois", body_style), Paragraph("Ingénieur DevOps", body_style)],
        [Paragraph("OX-005", body_style), Paragraph("Claire Moreau", body_style), Paragraph("Responsable Produit", body_style)],
    ]
    t = Table(table_data, colWidths=[100, 180, 220])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EFF6FF')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # 2. Architecture Visual Front-Office
    story.append(Paragraph("2. Ergonomie & Disposition 3-Colonnes Fullscreen", h2_style))
    story.append(Paragraph(
        "L'interface est structurée en 3 colonnes ajustables (100% Fullscreen, responsive PC/Tablette/Mobile) :<br/>"
        "• <b>Panneau Gauche (280px) :</b> Navigation par onglets (CHATS, CONTACTS, FAVORIS), barre de recherche dynamique, liste des salons et indicateurs de statut en ligne.<br/>"
        "• <b>Panneau Central (Flex 1) :</b> Flux de discussion instantanée avec bulles de messages pastel différenciées (bleu doux pour l'expéditeur, sable pour le destinataire) et barre d'outils de saisie.<br/>"
        "• <b>Panneau Droit (320px) :</b> Carte de profil utilisateur (nom + fonction), gestionnaire d'appels vidéo/audio en direct et galeries de médias partagés.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # 3. Audio & Video Calling Specifications
    story.append(Paragraph("3. Spécifications des Appels Audio & Vidéo WebRTC", h2_style))
    story.append(Paragraph(
        "<b>• File d'attente (Calls Queue) :</b> Aucun popup intrusif. Lorsqu'un appel (audio ou vidéo) est démarré par un membre, il est instantanément répertorié dans la section <i>APPELS EN COURS</i> du panneau droit avec le titre, le type d'appel et le nombre de participants.<br/>"
        "<b>• Rejoindre un appel :</b> N'importe quel membre présent dans le salon peut cliquer sur <i>Rejoindre</i> pour intégrer la session en cours.<br/>"
        "<b>• Affichage Multi-Participants :</b> Pour les appels vidéo comprenant 3 participants ou plus, l'interface génère dynamiquement une grille vidéo adaptative (Grid System 4:3) affichant les caméras de chaque participant en temps réel.<br/>"
        "<b>• Règle de Fin d'Appel :</b> Lorsqu'un participant secondaire quitte l'appel, la session reste active pour les autres. En revanche, si le créateur/organisateur de l'appel quitte, la session est fermée pour tous les participants.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # 4. Emojis and Media Management
    story.append(Paragraph("4. Sélecteur d'Emojis & Gestion des Fichiers Partagés", h2_style))
    story.append(Paragraph(
        "<b>• Emojis :</b> Popover interactif accessible depuis l'icône smile intégrant les émojis les plus populaires pour une insertion fluide dans le champ de texte.<br/>"
        "<b>• Partage de Médias & Stockage :</b> Prise en charge des images (PNG, JPG, GIF, WebP) avec prévisualisation agrandissable et des documents (PDF, XLSX, DOCX) téléchargeables.<br/>"
        "<b>• Galeries Initiales Vides :</b> Au chargement d'un salon, les sections <i>SHARED FILES</i> et <i>SHARED PHOTOS</i> du panneau droit commencent vides et se mettent à jour dynamiquement au fil de la conversation.",
        body_style
    ))

    doc.build(story)
    print("PDF généré avec succès : SPEC_TECHNIQUE_FRONTOFFICE.pdf")

if __name__ == "__main__":
    generate_pdf()
