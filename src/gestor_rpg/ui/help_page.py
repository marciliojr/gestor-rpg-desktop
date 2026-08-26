from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

SECTIONS: list[tuple[str, str, str, list[str]]] = [
    (
        "Começar",
        "Abra uma campanha antes de fichas, monstros, combate ou sessão.",
        "O Gestor RPG guarda tudo neste computador (SQLite). Não há conta, nuvem nem sincronização entre mesas.",
        [
            "Em Campanhas, clique em Nova, dê um nome e escolha o sistema: 3D&T Victory ou D&D 5e. O sistema não muda depois de salvar.",
            "Clique em Abrir campanha. O nome aparece na coluna esquerda e o subtítulo de cada página mostra Nome · sistema.",
            "Na próxima vez que abrir o app, a última campanha volta sozinha.",
            "Sem campanha aberta, Documentos e Dados ainda funcionam; o resto da mesa fica em espera.",
        ],
    ),
    (
        "A janela",
        "Três colunas fixas, sem menu de topo.",
        "Nada vai para uma barra superior. Ações de cada página ficam no miolo ou na lista da própria página.",
        [
            "Esquerda: marca, campanha aberta, grupos MESA / PREPARAR / JOGAR, FERRAMENTAS, Como usar e Sair.",
            "Centro: a página ativa (Campanhas, Fichas, Documentos, Monstros, Combate, Sessão ou esta ajuda).",
            "Direita: painel de Dados (rolagens). Na página Combate, o mapa aparece acima dos dados no mesmo painel.",
            "Listas escuras (mesas, personagens, manuais, catálogo, log) são o índice da página. A iniciativa em Combate é o painel claro.",
        ],
    ),
    (
        "Campanhas",
        "A mesa: nome, sistema, notas e backup.",
        "Uma campanha é o recipiente de fichas, encontros, log de sessão e posições no mapa.",
        [
            "Nova, Salvar e Excluir ficam na lista MESAS. Abrir campanha é o botão principal dos detalhes.",
            "Exportar JSON… grava o backup gestor-rpg-campaign-v1 (fichas, encontros, log da sessão e tokens no grid).",
            "Exportar PDF… gera um documento da mesa (elenco, fichas, combates, sessão e manuais).",
            "Importar JSON… lê esse backup e abre a mesa importada.",
            "Excluir apaga a campanha e tira ela de aberta, se era a atual.",
        ],
    ),
    (
        "Fichas",
        "PCs, NPCs e monstros da campanha aberta.",
        "A ficha segue o recorte do sistema. Victory usa P, H, R e os pools PA / PV / PM (sem Armadura nem PdF). D&D 5e usa o recorte 5e já no app.",
        [
            "Novo PC, Novo NPC ou um monstro vindo da página Monstros entram na lista PERSONAGENS.",
            "Buscar filtra pelo texto das fichas (Enter no campo ou o botão Buscar). Limpar volta a lista completa.",
            "Trocar de ficha grava em silêncio e não trava em erro. Só o botão Salvar ficha valida os campos.",
            "Exportar PDF… e Imprimir… geram a ficha do Gestor, não preenchem a ficha oficial do sistema.",
        ],
    ),
    (
        "Documentos",
        "Manuais e PDFs com busca no texto.",
        "Os documentos são por sistema. Sem campanha, a lista mostra manuais de todos os sistemas.",
        [
            "Importar PDF… (nesta página ou em FERRAMENTAS) escolhe o arquivo, o tipo (Ficha, Manual ou Outro) e o sistema.",
            "Extrair lê o texto; se a página vier como imagem, o app tenta OCR. Importar guarda o texto para busca.",
            "Se o tipo for Ficha e o PDF for reconhecido, dá para criar a ficha na campanha aberta. Se não reconhecer, o manual entra mesmo assim.",
            "Buscar (Enter) acha trechos. Abrir arquivo abre o PDF original neste computador. Excluir tira o documento da biblioteca.",
        ],
    ),
    (
        "Monstros",
        "Catálogo do sistema e gerador aleatório.",
        "Victory traz 47 desafios do compêndio local (P, H, R e PV; desafios sem PM/PA). D&D 5e traz 109 entradas (tabela de 100 + fichas detalhadas do anexo; stats completos só onde o texto traz CA/PV/atributos).",
        [
            "Filtre o CATÁLOGO por busca, tipo/origem, habitat/escala e poder. Clique uma linha para ver a ficha; duplo clique (ou Usar ficha do catálogo) copia para o editor.",
            "Gerar aleatório sorteia dentro dos filtros. Salvar na campanha grava como personagem do tipo monstro.",
            "A lista à esquerda são os monstros já salvos nesta mesa. Excluir selecionado remove só essa entrada.",
        ],
    ),
    (
        "Combate",
        "Iniciativa, pools e histórico de encontros.",
        "Cada campanha tem encontros. O combo no topo troca o combate; Novo combate guarda o atual no histórico.",
        [
            "Adicione da lista de PERSONAGENS ou um combatente avulso pelo nome.",
            "Rolar iniciativa usa 1d20 + bônus do sistema (na ficha). Próximo turno avança o marcador e a rodada.",
            "A ficha compacta mostra uma linha por pool: PV (ou HP) atual / máximo, e PM/PA ou Recurso conforme o plugin. Dano e Cura usam a quantidade ao lado.",
            "Em D&D 5e a lista mostra HP e Recurso, nunca PM/PA. Combatente com PV 0 aparece riscado.",
            "Excluir encontro apaga aquele combate e os combatentes dele. O app cria outro se a mesa ficar sem encontro.",
        ],
    ),
    (
        "Mapa",
        "Grid simples de tokens, só na página Combate.",
        "Não há paredes, visão nem dungeon. Casas A1, B2… no painel direito, acima dos dados.",
        [
            "Personagens da campanha são tokens aliados; avulsos são tokens rivais.",
            "Arraste o token para outra casa. Clique numa casa vazia para mover o combatente selecionado.",
            "Colunas e linhas (4–24 × 4–16) redimensionam o tabuleiro e prendem quem sairia da borda.",
            "A roda do mouse dá zoom e trava o enquadramento. Ajustar zoom volta a caber o mapa no painel.",
        ],
    ),
    (
        "Sessão",
        "Log da mesa, XP e tesouro.",
        "Cada entrada pode apontar para um encontro do histórico de Combate.",
        [
            "Nova começa um registro em branco. Salvar grava título (obrigatório), texto, XP e tesouro.",
            "Excluir tira a entrada do log. O backup da campanha inclui esse log.",
        ],
    ),
    (
        "Dados",
        "O painel direito vale em qualquer página.",
        "Rolar é a ação principal. O número grande é o total; abaixo, o detalhe (por exemplo 3d6 [2, 5, 1] +2).",
        [
            "Escreva uma expressão (3d6+2, 1d20+1d4-1) e pressione Enter ou Rolar. Faces permitidas: d4, d6, d8, d10, d12, d20 e d100.",
            "Os atalhos d4…d100 rolam 1 dado daquela face na hora.",
            "Clique uma linha do histórico para rerrolar a mesma expressão. Limpar histórico apaga as rolagens salvas.",
        ],
    ),
    (
        "Ferramentas",
        "Atalhos globais, à esquerda, abaixo de JOGAR.",
        "Não repetem as ações de cada página (exportar ficha, mapa, combo de encontro ficam onde a mesa acontece).",
        [
            "NPC rápido… gera nome, motivação, gancho e ficha do sistema escolhido. Salvar na campanha exige mesa aberta no mesmo sistema.",
            "Gerador de nomes… sorteia Medieval, Élfico, Anão ou Oriental (completo, prenome, sobrenome ou apelido) e copia o selecionado.",
            "Importar PDF… é o mesmo fluxo da página Documentos.",
            "Como usar abre esta tela. Sair fica no rodapé da barra, fora das ferramentas.",
        ],
    ),
    (
        "Sistemas",
        "A mesa usa 3D&T Victory ou D&D 5e.",
        "O sistema é escolhido ao criar a campanha e não muda depois.",
        [
            "Victory: P, H, R, PA, PV e PM. Desafios do catálogo vêm com PV da ficha, sem PM/PA.",
            "D&D 5e: HP e Recurso (espaços/outros).",
            "O app não substitui o livro: catálogos usam só os compêndios locais.",
        ],
    ),
]


def _heading(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("helpHeading")
    label.setWordWrap(True)
    return label


def _body(text: str, *, lead: bool = False) -> QLabel:
    label = QLabel(text)
    label.setObjectName("helpLead" if lead else "helpBody")
    label.setWordWrap(True)
    label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    return label


def _card(title: str, lead: str, intro: str, steps: list[str]) -> QWidget:
    card = QWidget()
    card.setObjectName("helpCard")
    layout = QVBoxLayout(card)
    layout.setContentsMargins(16, 14, 16, 14)
    layout.setSpacing(6)
    layout.addWidget(_heading(title))
    layout.addWidget(_body(lead, lead=True))
    layout.addWidget(_body(intro))
    for step in steps:
        layout.addWidget(_body(f"• {step}"))
    return card


class HelpPage(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        title = QLabel("Como usar")
        title.setObjectName("pageTitle")
        root.addWidget(title)
        hint = QLabel("Gestor RPG 1.0  ·  mesa local  ·  3D&T Victory e D&D 5e")
        hint.setObjectName("pageSubtitle")
        root.addWidget(hint)

        splitter = QSplitter()
        toc_box = QWidget()
        toc_box.setObjectName("sidePanel")
        toc_l = QVBoxLayout(toc_box)
        toc_l.setContentsMargins(12, 12, 12, 12)
        toc_l.setSpacing(10)
        section = QLabel("ÍNDICE")
        section.setObjectName("sectionTitle")
        toc_l.addWidget(section)
        self.toc = QListWidget()
        self.toc.setObjectName("helpToc")
        for title_text, *_rest in SECTIONS:
            self.toc.addItem(QListWidgetItem(title_text))
        self.toc.currentRowChanged.connect(self._jump)
        toc_l.addWidget(self.toc, 1)
        splitter.addWidget(toc_box)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body = QWidget()
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(12, 0, 4, 12)
        body_l.setSpacing(12)
        self._anchors: list[QWidget] = []
        for title_text, lead, intro, steps in SECTIONS:
            card = _card(title_text, lead, intro, steps)
            self._anchors.append(card)
            body_l.addWidget(card)
        body_l.addStretch(1)
        self.scroll.setWidget(body)
        splitter.addWidget(self.scroll)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        root.addWidget(splitter, 1)
        self.toc.setCurrentRow(0)

    def _jump(self, row: int) -> None:
        if not (0 <= row < len(self._anchors)):
            return
        self.scroll.ensureWidgetVisible(self._anchors[row], 0, 20)
