"""Catálogo de desafios 3D&T Victory (compêndio local).

Fonte: fichas-monstros-3det.md (P, H, R e PV da ficha; desafios sem PM/PA).
"""

from __future__ import annotations

from typing import Any

CATEGORIES: list[tuple[str, str]] = [
    ("masmorras", "Masmorras & Marmitas"),
    ("sombria", "Fantasia Sombria"),
    ("mitica", "Fantasia Mítica"),
    ("epica", "Fantasia Épica"),
    ("ajudantes", "Ajudantes"),
    ("ferozes", "Ferozes e Furiosos"),
]

ESCALAS = ("Ningen", "Sugoi", "Kiodai")
POWER_LABELS = {
    "fraco": "Fraco",
    "medio": "Médio",
    "forte": "Forte",
    "lendario": "Lendário",
}

BESTIARY: list[dict[str, Any]] = [
  {
    "id": 1,
    "slug": "criatura-resetada",
    "name": "Criatura Resetada",
    "points": 10,
    "power": "medio",
    "escala": "Ningen",
    "category": "masmorras",
    "category_label": "Masmorras & Marmitas",
    "origem": "Era das Arcas / Masmorras & Marmitas",
    "poder": 4,
    "habilidade": 2,
    "resistencia": 3,
    "pv": 15,
    "pericias": [
      "Luta"
    ],
    "vantagens": [],
    "desvantagens": [],
    "poderes": [
      "Sou o monstrão mesmo: A criatura resetada recebe um poder único de monstro, escolhido pelo mestre (Manual 3DeT Victory, p. 213 ou qualquer outro poder único deste livro que você achar legal). Ela não ficou mais forte por acaso. Ficou por experiência."
    ],
    "tesouro": "Nocivo ou sob medida.",
    "notas": [],
  },
  {
    "id": 2,
    "slug": "grande-inimigo-apelao",
    "name": "Grande Inimigo Apelão",
    "points": 25,
    "power": "forte",
    "escala": "Ningen",
    "category": "masmorras",
    "category_label": "Masmorras & Marmitas",
    "origem": "Masmorras & Marmitas",
    "poder": 6,
    "habilidade": 4,
    "resistencia": 6,
    "pv": 30,
    "pericias": [
      "Luta",
      "Mística"
    ],
    "vantagens": [],
    "desvantagens": [
      "Fraqueza (só o mestre sabe qual é)"
    ],
    "poderes": [
      "Ataque apelão: Sempre que sofre qualquer ataque que causa dano, o Grande Inimigo Apelão reage imediatamente, atacando o responsável. Sim. Se sofre cinco ataques na rodada, ele contra-ataca cinco vezes. Pense bem antes de fazer aquele ataque extra.",
      "Defesa apelona: Não basta estar uma escala acima. Se a defesa do Grande Inimigo é maior que o ataque recebido, o atacante sofre dano igual à diferença. Aqui, errar machuca.",
      "Poder apelão: Ao final de cada rodada, o Grande Inimigo Apelão realiza um ataque adicional que também atinge todos Perto. Mesmo depois de contra-atacar inúmeras vezes, ele ainda apela mais um pouco. Porque pode."
    ],
    "tesouro": "Artefato apelão de até 10XP (Manual 3DeT Victory, p. 138).",
    "notas": [],
  },
  {
    "id": 3,
    "slug": "mandragora",
    "name": "Mandrágora",
    "points": 6,
    "power": "fraco",
    "escala": "Ningen",
    "category": "masmorras",
    "category_label": "Masmorras & Marmitas",
    "origem": "Masmorras & Marmitas",
    "poder": 1,
    "habilidade": 1,
    "resistencia": 2,
    "pv": 10,
    "pericias": [],
    "vantagens": [],
    "desvantagens": [
      "Lento",
      "Inculto (descritivo)"
    ],
    "poderes": [
      "Raízes Teimosas: Desenterrar uma mandrágora exige uma ação completa e um teste de Esporte ou Sobrevivência (meta 9). A diaba grita imediatamente quando isso acontece.",
      "Cagueta: O grito da mandrágora pode ser ouvido praticamente na masmorra inteira, potencialmente atraindo outros encontros com monstros aleatórios."
    ],
    "tesouro": "Seiva de Mandrágora: Cada criatura rende um frasco. Usado para preparar uma refeição, dobra seu efeito ou duração. Usado para negociar, eleva o teste de compra uma escala.",
    "notas": [
      "Atributos: `P1, H1, R2 (Estimados com base na pontuação)`",
      "Recursos: `10 (Estimados com base na pontuação) PV` (Desafios não possuem PM ou PA)"
    ],
  },
  {
    "id": 4,
    "slug": "engolidor-de-luz",
    "name": "Engolidor de Luz",
    "points": 11,
    "power": "medio",
    "escala": "Ningen",
    "category": "masmorras",
    "category_label": "Masmorras & Marmitas",
    "origem": "Masmorras & Marmitas",
    "poder": 2,
    "habilidade": 2,
    "resistencia": 4,
    "pv": 20,
    "pericias": [
      "Mística"
    ],
    "vantagens": [
      "Incorpóreo"
    ],
    "desvantagens": [
      "Monstruoso (descritivo)"
    ],
    "poderes": [
      "Senhor do Escuro: O engolidor tem Ganho em todos os testes quando o ambiente está em escuridão total. Se oponentes trouxerem tochas ou luz, ele tenta consumi-las."
    ],
    "tesouro": "Luz Engarrafada: Cada dose (1D), quando liberada, ilumina completamente um aposento de qualquer tamanho durante uma cena — potencialmente acabando com a alegria do ladino que tentava se esconder.",
    "notas": [],
  },
  {
    "id": 5,
    "slug": "rastejante-de-pedra",
    "name": "Rastejante de Pedra",
    "points": 12,
    "power": "medio",
    "escala": "Ningen",
    "category": "masmorras",
    "category_label": "Masmorras & Marmitas",
    "origem": "Masmorras & Marmitas",
    "poder": 3,
    "habilidade": 1,
    "resistencia": 4,
    "pv": 20,
    "pericias": [
      "Sobrevivência (esconder-se nas masmorras)"
    ],
    "vantagens": [
      "Arena (Subterrâneos)",
      "Sentido (Radar)"
    ],
    "desvantagens": [
      "Lento",
      "Monstruoso"
    ],
    "poderes": [
      "Mimetismo mineral: Massa mineral sem olhos nem forma definida, que se mistura às paredes e observa com fendas microscópicas. O ataque é lento, mas incessante.",
      "Guincho Dissipante: Quando sofre qualquer dano, o rastejante emite um rosnado desencantador. Todos os personagens até Longe fazem um teste de Resistência (9) para não perder 1D PM."
    ],
    "tesouro": "Coração de Rocha Viva: Fragmento pulsante que vibra levemente quando há inimigos por perto. Uma vez por cena, concede Ganho em um teste de iniciativa.",
    "notas": [
      "Atributos: `P3, H1, R4 (Estimados com base na pontuação e descrição)`",
      "Recursos: `20 (Estimados com base na pontuação) PV` (Desafios não possuem PM ou PA)"
    ],
  },
  {
    "id": 6,
    "slug": "sanguessuga-de-armadura",
    "name": "Sanguessuga de Armadura",
    "points": 12,
    "power": "medio",
    "escala": "Ningen",
    "category": "masmorras",
    "category_label": "Masmorras & Marmitas",
    "origem": "Masmorras & Marmitas",
    "poder": 3,
    "habilidade": 2,
    "resistencia": 4,
    "pv": 20,
    "pericias": [
      "Luta",
      "Sobrevivência"
    ],
    "vantagens": [],
    "desvantagens": [
      "Diferente (armadura oca)"
    ],
    "poderes": [
      "Cavaleiro Oco: Enquanto escorrega pra cá e pra lá dentro da armadura, a sanguessuga é bem difícil de acertar — ataques contra ela sempre têm Perda. Apenas ataques com fogo ou magia ignoram esse efeito."
    ],
    "tesouro": "Gosma da Persistência: 1D+1 frascos cheios de parasita adormecido, usados como consumível. Aprimora seus equipamentos metálicos de combate (+1 em testes de Luta) durante uma cena.",
    "notas": [],
  },
  {
    "id": 7,
    "slug": "mimico",
    "name": "Mímico",
    "points": 14,
    "power": "medio",
    "escala": "Ningen",
    "category": "masmorras",
    "category_label": "Masmorras & Marmitas",
    "origem": "Masmorras & Marmitas",
    "poder": 3,
    "habilidade": 4,
    "resistencia": 3,
    "pv": 10,
    "pericias": [
      "Luta",
      "Manha"
    ],
    "vantagens": [
      "Adesivo Vivente (descrito em regras)",
      "Inofensivo (enquanto disfarçado)"
    ],
    "desvantagens": [
      "Diferente"
    ],
    "poderes": [
      "Surpresa!: O mímico tem Ganho em testes de Manha para fingir ser um objeto inanimado (como arcas, baús e relicários) e também em ataques contra alvos com iniciativa abaixo da sua.",
      "Adesivo Vivente: O mímico é uma massaroca de dentes e tentáculos cobertos de gosma pegajosa. Ele sempre tem Ganho em manobras de agarrão.",
      "Abocanhar: Quando o mímico ataca e consegue um crítico, além de causar dano, seu ataque também é considerado um agarrão (Manual 3DeT Victory, p. 171). Um personagem agarrado, além de ficar imobilizado, também sofre 2D de dano por turno. Um personagem derrotado desta forma é engolido; só pode ser salvo com a derrota do mímico.",
      "Mimimímico: Quando um mímico é encontrado, existe chance (5 ou 6 em 1D) de ser uma versão Sugoi por ter sobrevivido a aventureiros de alto nível."
    ],
    "tesouro": "Itens devorados ou restos digeridos em seu interior.",
    "notas": [],
  },
  {
    "id": 8,
    "slug": "dragourmet",
    "name": "Dragourmet",
    "points": 35,
    "power": "forte",
    "escala": "Ningen",
    "category": "masmorras",
    "category_label": "Masmorras & Marmitas",
    "origem": "Altas Aventuras / Masmorras & Marmitas",
    "poder": 4,
    "habilidade": 2,
    "resistencia": 7,
    "pv": 35,
    "pericias": [
      "Arte",
      "Luta",
      "Sobrevivência"
    ],
    "vantagens": [
      "Alcance 1",
      "Brutal (Vida)",
      "Sentido (Paladar Aguçado)",
      "Vigoroso",
      "Voo"
    ],
    "desvantagens": [
      "Maldição (não ataca quem carrega panelas ou ingredientes — não por bondade, mas porque “mão de obra não se desperdiça”)"
    ],
    "poderes": [
      "Apetite insaciável: O Dragourmet não resiste a um pedacinho extra de vítimas mais suculentas. Ao atacar personagens com R3 ou mais, sua vantagem Brutal recupera 1PV para cada 2 pontos de dano causado.",
      "Sopro flambado: Sempre que rola um ou mais críticos no teste de ataque, este também é considerado como Ataque Especial (Penetrante).",
      "Vergonha da profissão!: Um oponente pode tentar preparar um prato melhor que o Dragourmet (ou convencê-lo disso). Para isso, realiza um teste resistido de Arte, Influência ou Sobrevivência contra Arte ou Sobrevivência do Dragourmet. Quem falha sofre Perda em todos os testes contra o adversário até o fim da cena."
    ],
    "tesouro": "Couro ou dentes exóticos (além de ingredientes culinários lendários).",
    "notas": [],
  },
  {
    "id": 9,
    "slug": "colosso",
    "name": "Colosso",
    "points": 16,
    "power": "medio",
    "escala": "Kiodai",
    "category": "masmorras",
    "category_label": "Masmorras & Marmitas",
    "origem": "Masmorras & Marmitas",
    "poder": 9,
    "habilidade": 1,
    "resistencia": 12,
    "pv": 60,
    "pericias": [
      "Sobrevivência"
    ],
    "vantagens": [
      "Forte",
      "Vigoroso"
    ],
    "desvantagens": [
      "Diferente",
      "Tapado"
    ],
    "poderes": [
      "Elefante em loja de cristais: Para o Colosso, tudo até Longe é considerado Perto. Além disso, todos os seus ataques são considerados Ataque Especial (Área)."
    ],
    "tesouro": "Ossos colossais ou fragmentos antigos.",
    "notas": [],
  },
  {
    "id": 10,
    "slug": "carcaca-funesta",
    "name": "Carcaça Funesta",
    "points": 11,
    "power": "medio",
    "escala": "Ningen",
    "category": "sombria",
    "category_label": "Fantasia Sombria",
    "origem": "Fantasia Sombria",
    "poder": 4,
    "habilidade": 1,
    "resistencia": 4,
    "pv": 20,
    "pericias": [
      "Luta",
      "Percepção"
    ],
    "vantagens": [
      "Resoluto",
      "Vigoroso (esqueleto animado)"
    ],
    "desvantagens": [
      "Dependência (comer carne de criaturas vivas)",
      "Monstruoso"
    ],
    "poderes": [
      "Terror de Ferro: Carcaças Funestas não são simples zumbis ou esqueletos reanimados. Seus corpos mortos-vivos são o resultado da negação violenta da morte por parte de um guerreiro que perdeu tudo, menos a armadura. É um amontoado brutal de corpos e ossos de outros caídos."
    ],
    "tesouro": "Arma Mágica: Role 1D. Com um 6, cai uma arma com uma qualidade à escolha do mestre (Manual 3DeT Victory, p. 139).",
    "notas": [
      "Atributos: `P4, H1, R4 (Estimados com base na pontuação)`"
    ],
  },
  {
    "id": 11,
    "slug": "gula-do-inferno-carcaca-funesta",
    "name": "Gula do Inferno (Carcaça Funesta)",
    "points": 21,
    "power": "forte",
    "escala": "Ningen",
    "category": "sombria",
    "category_label": "Fantasia Sombria",
    "origem": "Fantasia Sombria",
    "poder": 5,
    "habilidade": 1,
    "resistencia": 5,
    "pv": 125,
    "pericias": [
      "Luta",
      "Percepção"
    ],
    "vantagens": [
      "+Vida 10"
    ],
    "desvantagens": [
      "Dependência (comer criaturas vivas)"
    ],
    "poderes": [
      "Debater Desesperado: Enquanto tiver metade ou menos de seus PV, seus ataques atingem todos os inimigos Perto. Além disso, uma vez por cena, quando Gula do Inferno usa esse poder, o Dado do Medo aumenta em 1.",
      "Mastigar Tudo: Pode gastar uma ação completa para fazer um ataque equivalente a um Ataque Especial (Poderoso, Titânico). Além disso, uma vez por cena, quando Gula do Inferno usa esse poder, o Dado do Medo aumenta em 1.",
      "Revelar a Verdade: Pode gastar uma ação completa para revelar os pecados e as culpas de todos os alvos até Longe, fazendo o Dado do Medo aumentar em 1."
    ],
    "tesouro": "Arma Mágica: Role 1D. Com um 6, cai uma arma com a qualidade à escolha do mestre (Manual 3DeT Victory, p. 139).",
    "notas": [],
  },
  {
    "id": 12,
    "slug": "sacerdote-sem-rosto",
    "name": "Sacerdote Sem Rosto",
    "points": 13,
    "power": "medio",
    "escala": "Ningen",
    "category": "sombria",
    "category_label": "Fantasia Sombria",
    "origem": "Fantasia Sombria",
    "poder": 3,
    "habilidade": 2,
    "resistencia": 3,
    "pv": 15,
    "pericias": [
      "Influência",
      "Mística"
    ],
    "vantagens": [
      "Calma Inabalável",
      "Magia"
    ],
    "desvantagens": [
      "Monstruoso (máscara de carne lisa)",
      "Devoto"
    ],
    "poderes": [
      "Converter Pessoa: Ele não é mais um homem, mas o vácuo deixado por uma adoração absoluta de um deus apagado. Pode gastar uma ação completa para converter um NPC nas redondezas para sua procissão de almas acorrentadas. Se fizer isso, cura a procissão em 2D."
    ],
    "tesouro": "Acessório dos Fiéis: Role 1D. Com 5 ou 6, cai um acessório com a qualidade Obra-Prima (Manual 3DeT Victory, p. 140).",
    "notas": [
      "Atributos: `P3, H2, R3 (Estimados com base na pontuação)`",
      "Recursos: `15 (Estimados) PV` (Desafios não possuem PM ou PA)"
    ],
  },
  {
    "id": 13,
    "slug": "orochi",
    "name": "Orochi",
    "points": None,
    "power": "lendario",
    "escala": "Sugoi",
    "category": "mitica",
    "category_label": "Fantasia Mítica",
    "origem": "Fantasia Mítica",
    "poder": 0,
    "habilidade": 2,
    "resistencia": 9,
    "pv": 105,
    "pericias": [
      "Luta",
      "Percepção"
    ],
    "vantagens": [
      "Corpo: +Vida 6",
      "Vigoroso | Cabeças: Ágil",
      "Alcance 1",
      "+Vida 3"
    ],
    "desvantagens": [
      "Corpo: Lento"
    ],
    "poderes": [
      "Cabeças Orochi: Orochi tem oito cabeças encimando longos pescoços serpentinos. Em cada rodada, até três delas podem agir. Além de morder, cada uma pode causar uma pequena catástrofe natural:",
      "Explosão de Fogo: Ataque com P+6 contra todos os alvos Perto. Quem sofrer dano maior que a Resistência fica em chamas e sofre metade do dano novamente na rodada seguinte.",
      "Furacão: Ataque com P+6 contra todos os alvos Perto. Quem sofre dano maior que sua Resistência fica caído, com Perda em todos os testes até usar um movimento para se levantar.",
      "Maremoto: Ataque com P+2 contra todos os alvos Muito Longe. Quem sofre dano maior que sua Resistência fica caído, com Perda em todos os testes até usar um movimento para se levantar.",
      "Nevasca: Ataque com P+4 contra todos os alvos Longe. Quem sofre dano maior que sua Resistência fica paralisado por uma rodada."
    ],
    "tesouro": "Couro de Serpente Divina (30XP) (forja armaduras R+2) ou Espada Misteriosa (40XP) (encontrada no esôfago de uma cabeça, bônus Poder +2 em testes de ataque e qualidade Espiritual).",
    "notas": [
      "Atributos: `Corpo: P-, H2, R9 | Cabeças (x8): P6, H3, R6`",
      "Recursos: `Corpo: 105 PV | Cabeças (x8): 60 PV cada PV` (Desafios não possuem PM ou PA)"
    ],
    "poder_alt": 6,
  },
  {
    "id": 14,
    "slug": "agnikhan-o-espirito-do-fogo",
    "name": "Agnikhan, o Espírito do Fogo",
    "points": 10,
    "power": "medio",
    "escala": "Ningen",
    "category": "ajudantes",
    "category_label": "Ajudantes",
    "origem": "Fantasia Épica / Ajudantes Conjurados",
    "poder": 3,
    "habilidade": 2,
    "resistencia": 2,
    "pv": 10,
    "pericias": [
      "Luta",
      "Mística"
    ],
    "vantagens": [
      "Brutal (Mana)",
      "Magia"
    ],
    "desvantagens": [
      "Vulnerável (Água)",
      "Inculto"
    ],
    "poderes": [
      "Companheiro Conjurado: Você pode gastar uma ação completa para invocar Agnikhan como Companheiro (20 XP) até o fim do combate ou cena."
    ],
    "tesouro": "Faísca da Alma: 1D+1 faíscas. Quando faz um ataque, você pode gastar uma faísca para causar dano de fogo e impor Perda no teste de defesa do alvo.",
    "notas": [
      "Atributos: `P3, H2, R2 (Estimados com base na pontuação)`"
    ],
  },
  {
    "id": 15,
    "slug": "holle-a-princesa-do-inverno",
    "name": "Holle, a Princesa do Inverno",
    "points": 10,
    "power": "medio",
    "escala": "Ningen",
    "category": "ajudantes",
    "category_label": "Ajudantes",
    "origem": "Fantasia Épica / Ajudantes Conjurados",
    "poder": 2,
    "habilidade": 3,
    "resistencia": 2,
    "pv": 10,
    "pericias": [
      "Animais",
      "Mística"
    ],
    "vantagens": [
      "Paralisia",
      "Voo"
    ],
    "desvantagens": [
      "Fraqueza (Fogo)",
      "Inculto"
    ],
    "poderes": [
      "Companheira Conjurada: Você pode gastar uma ação completa para invocar Holle como Companheira (20 XP) até o fim do combate ou cena."
    ],
    "tesouro": "Cristal de Gelo / Ajudante Conjurada: 1D+1 cristais. Ao fazer um ataque, você pode gastar um cristal para causar dano de frio e impor Perda no teste de defesa.",
    "notas": [
      "Atributos: `P2, H3, R2 (Estimados)`"
    ],
  },
  {
    "id": 16,
    "slug": "leishen-o-sabio-da-tempestade",
    "name": "Leishen, o Sábio da Tempestade",
    "points": 10,
    "power": "medio",
    "escala": "Ningen",
    "category": "ajudantes",
    "category_label": "Ajudantes",
    "origem": "Fantasia Épica / Ajudantes Conjurados",
    "poder": 2,
    "habilidade": 3,
    "resistencia": 2,
    "pv": 10,
    "pericias": [
      "Mística",
      "Saber"
    ],
    "vantagens": [
      "Alcance 1",
      "Magia"
    ],
    "desvantagens": [
      "Código dos Enigmas",
      "Inculto"
    ],
    "poderes": [
      "Companheiro Conjurado: Você pode gastar uma ação completa para invocar Leishen como Companheiro (20 XP) até o fim do combate ou cena."
    ],
    "tesouro": "Relâmpago Cristalizado: 1D+1 relâmpagos. Ao fazer um ataque, você pode gastar um relâmpago para causar dano de choque e impor Perda no teste de defesa.",
    "notas": [
      "Atributos: `P2, H3, R2 (Estimados)`"
    ],
  },
  {
    "id": 17,
    "slug": "solskaan-o-dragao-do-sol",
    "name": "Solskaan, o Dragão do Sol",
    "points": 20,
    "power": "forte",
    "escala": "Sugoi",
    "category": "ajudantes",
    "category_label": "Ajudantes",
    "origem": "Fantasia Épica / Ajudantes Conjurados",
    "poder": 4,
    "habilidade": 3,
    "resistencia": 3,
    "pv": 20,
    "pericias": [
      "Luta",
      "Percepção"
    ],
    "vantagens": [
      "Sentido (Visão Aguçada)",
      "Voo",
      "Alcance 1"
    ],
    "desvantagens": [
      "Diferente",
      "Inculto"
    ],
    "poderes": [
      "Sopro de Luz: Uma vez por combate ou cena, você pode gastar uma ação e 3PM para disparar um sopro de luz que atinge todos até Longe."
    ],
    "tesouro": "Escama Solar / Ajudante Conjurado: 1D+1 escamas. Ao atacar, você pode gastar uma escama para causar dano de luz e impor Perda no teste de defesa.",
    "notas": [
      "Atributos: `P4, H3, R3 (Estimados com base na escala e bônus)`",
      "Recursos: `20 (Estimados) PV` (Desafios não possuem PM ou PA)"
    ],
  },
  {
    "id": 18,
    "slug": "vulkuran-a-montanha-viva",
    "name": "Vulkuran, a Montanha Viva",
    "points": 20,
    "power": "forte",
    "escala": "Sugoi",
    "category": "ajudantes",
    "category_label": "Ajudantes",
    "origem": "Fantasia Épica / Ajudantes Conjurados",
    "poder": 4,
    "habilidade": 1,
    "resistencia": 5,
    "pv": 25,
    "pericias": [
      "Luta",
      "Sobrevivência"
    ],
    "vantagens": [
      "Resoluto",
      "Vigoroso",
      "Defesa Especial"
    ],
    "desvantagens": [
      "Lento",
      "Inculto"
    ],
    "poderes": [
      "Muralha Rochosa: Com um movimento, Vulkuran faz a terra erguer-se em sua defesa. Ele e todos os aliados até Longe recebem Ganho e um crítico automático em seu próximo teste de defesa."
    ],
    "tesouro": "Granito Brilhante / Ajudante Conjurado (10 XP) / Companheiro (20 XP): 1D+1 pedras. Ao fazer um teste de defesa, você pode gastar uma pedra para receber Ganho.",
    "notas": [
      "Atributos: `P4, H1, R5 (Estimados com base no papel de tanque)`",
      "Recursos: `25 (Estimados) PV` (Desafios não possuem PM ou PA)"
    ],
  },
  {
    "id": 19,
    "slug": "trobo",
    "name": "Trobo",
    "points": 1,
    "power": "fraco",
    "escala": "Ningen",
    "category": "ajudantes",
    "category_label": "Ajudantes",
    "origem": "Fantasia Épica / Ajudantes Trobos",
    "poder": 2,
    "habilidade": 1,
    "resistencia": 3,
    "pv": 15,
    "pericias": [
      "Esporte"
    ],
    "vantagens": [
      "Aceleração",
      "Vigoroso"
    ],
    "desvantagens": [
      "Inculto"
    ],
    "poderes": [
      "Animal de Tração: Usados como animais de carga em caravanas e fazendas, compensam menor velocidade com grande resistência física e capacidade de carga."
    ],
    "tesouro": "Charque de trobo (1D porções, cada uma permite preparar um carreteiro de bônus 5PV) ou Couro de trobo (10 XP) (concede R+1 em testes de defesa).",
    "notas": [],
  },
  {
    "id": 20,
    "slug": "mycelas-parasita-de-mundos",
    "name": "Mycelas, Parasita de Mundos",
    "points": 42,
    "power": "forte",
    "escala": "Kiodai",
    "category": "epica",
    "category_label": "Fantasia Épica",
    "origem": "Fantasia Épica",
    "poder": 8,
    "habilidade": 4,
    "resistencia": 6,
    "pv": 50,
    "pericias": [
      "Luta",
      "Sobrevivência"
    ],
    "vantagens": [
      "Sentido",
      "+Vida"
    ],
    "desvantagens": [
      "Monstruoso",
      "Inculto"
    ],
    "poderes": [
      "Nuvem Tóxica: Mycelas gasta uma ação completa para lançar esporos tóxicos sobre todo o campo de batalha, atacando todos até Muito Longe com P+6. Quem sofre dano faz um teste de Resistência (15); em caso de falha, fica enjoado, com Perda em todos os testes até ser curado. Usado com 50% de PV.",
      "Prender Alvo: Quando causa dano em um alvo, Mycelas pode gastar um movimento para agarrá-lo (Manual 3DeT Victory, p. 171). Ele pode manter até dois personagens agarrados.",
      "Tentáculos Farpados: Os ataques de Mycelas têm chance de crítico em 5 ou 6. Personagens que sofrem dano fazem um teste de Resistência (15). Em caso de falha, ficam envenenados e sofrem o mesmo dano novamente no início da próxima rodada."
    ],
    "tesouro": "Nenhum. O mundo foi salvo — isso já deveria ser tesouro mais que suficiente!",
    "notas": [
      "Atributos: `P8, H4, R6 (Estimados com base na ficha de 42pt Kiodai)`",
      "Recursos: `50 (Estimados) PV` (Desafios não possuem PM ou PA)"
    ],
  },
  {
    "id": 21,
    "slug": "arcanerd-aprendiz",
    "name": "Arcanerd Aprendiz",
    "points": 6,
    "power": "fraco",
    "escala": "Ningen",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 3,
    "habilidade": 3,
    "resistencia": 2,
    "pv": 10,
    "pericias": [
      "Mística"
    ],
    "vantagens": [
      "Alcance 1",
      "Gênio"
    ],
    "desvantagens": [
      "Antipático (descritivo)"
    ],
    "poderes": [
      "Barreira de Gelatina: Uma vez por cena, pode invocar uma barreira mágica… feita de gelatina mágica rosa, instável e escorregadia! Fornece +3 em testes de defesa até o fim da cena, mas, se rolar falha crítica na defesa, a gelatina explode e lambuza todos Perto.",
      "Invocação de Familiar Caótico: Uma vez por cena, pode conjurar um bichinho mágico aleatório (role 1D): 1: Pombo incandescente (Ajudante Lutador); 2-4: Peixe flutuante filosófico (Ajudante Especialista); 5-6: Minhoca com chapéu de bruxa (permite usar outra vez qualquer poder com um uso por cena)."
    ],
    "tesouro": "Ajudante: Aprendiz Deslumbrado (10XP) - Aluno do primeiro ano acompanha heróis. Escolha entre Familiar ou usar Magia uma vez sem gastar PM.",
    "notas": [],
  },
  {
    "id": 22,
    "slug": "arcanerd-graduando",
    "name": "Arcanerd Graduando",
    "points": 12,
    "power": "medio",
    "escala": "Ningen",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 3,
    "habilidade": 3,
    "resistencia": 3,
    "pv": 15,
    "pericias": [
      "Mística",
      "Saber"
    ],
    "vantagens": [
      "Alcance 1"
    ],
    "desvantagens": [
      "Código da Pesquisa",
      "Tapado (em interações)"
    ],
    "poderes": [
      "Orbe de Caos Colorido: Uma vez por cena, pode conjurar uma esfera mágica instável que gira com cores berrantes e sons incoerentes. Role um dado. Ímpar: 1D+2 de dano a todos os alvos Perto (exceto o Arcanerd). Par: o Arcanerd sofre um efeito cômico aleatório por 1 turno.",
      "Escudo de Teses Arcanas: Uma vez por turno, ao receber um ataque, pode fazer um teste de Mística como defesa, citando três autores célebres de magias defensivas.",
      "Transfiguração Autodramática: Pode, uma vez por combate, se transformar em um ser místico com +2 em todos os atributos até o fim da cena. O efeito termina se sofrer qualquer dano, ou se alguém disser: 'Tá, mas e o ataque?'"
    ],
    "tesouro": "Grimório de Ouro com Capítulo Proibido: Contém um dos poderes acima como técnica lendária.",
    "notas": [],
  },
  {
    "id": 23,
    "slug": "monge-de-ferro",
    "name": "Monge de Ferro",
    "points": 17,
    "power": "forte",
    "escala": "Ningen",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 5,
    "habilidade": 3,
    "resistencia": 5,
    "pv": 25,
    "pericias": [
      "Luta",
      "Percepção"
    ],
    "vantagens": [
      "Alcance 1",
      "Forte"
    ],
    "desvantagens": [
      "Diferente (Construto de elite)"
    ],
    "poderes": [
      "Olhar de Condenação: Uma vez por cena, o Monge perturba o coração de todos os adversários até Longe (mesmo efeito da vantagem Confusão, mas não exige ataque).",
      "Chicote de Julgamento: Seu ataque padrão, além de causar dano, derruba o alvo quando consegue um acerto crítico. Um personagem caído tem Perda em todos os testes. Levantar exige um movimento.",
      "Zona de Silêncio Opressor: O Monge emana continuamente um campo de anti-energia vital. Todas as criaturas até Longe, exceto construtos, sofrem Perda."
    ],
    "tesouro": "Rosário de Circuitos: Colar metálico com processadores em miniatura. Uma vez por sessão, permite refazer um teste de Influência ou Luta com Ganho.",
    "notas": [],
  },
  {
    "id": 24,
    "slug": "canideo-de-sepulcro",
    "name": "Canídeo de Sepulcro",
    "points": 11,
    "power": "medio",
    "escala": "Ningen",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 3,
    "habilidade": 4,
    "resistencia": 2,
    "pv": 10,
    "pericias": [
      "Luta",
      "Sobrevivência"
    ],
    "vantagens": [
      "Ágil",
      "Sentido (Visão Aguçada)"
    ],
    "desvantagens": [
      "Inculto",
      "Diferente"
    ],
    "poderes": [
      "Investida Rasgante: Se usar um movimento para chegar Perto do alvo, ataca com Ganho.",
      "Código de Alcateia: Para cada Canídeo de Sepulcro na cena além do primeiro, todos ganham +1 em testes de ataque, até um máximo +5.",
      "Uivo de Eco: Uma vez por cena, pode uivar para causar medo em todos os inimigos até Longe. Estes sofrem Perda no próximo teste."
    ],
    "tesouro": "Presas de Carbono Negro: Fragmentos das mandíbulas. Uma vez por sessão concede Ganho em um ataque Perto.",
    "notas": [],
  },
  {
    "id": 25,
    "slug": "tecnossauro",
    "name": "Tecnossauro",
    "points": 26,
    "power": "forte",
    "escala": "Sugoi",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 4,
    "habilidade": 2,
    "resistencia": 4,
    "pv": 20,
    "pericias": [
      "Luta",
      "Percepção (descrito)"
    ],
    "vantagens": [
      "Forte",
      "Sentido (Infravisão, Faro Aguçado, Audição Aguçada)",
      "+Vida"
    ],
    "desvantagens": [
      "Inculto",
      "Monstruoso"
    ],
    "poderes": [
      "Mandíbula Hidráulica de Caçada: Sua mordida é considerada um Agarrão (Manual 3DeT Victory, p. 171), exceto que também causa dano — enquanto é agarrado, você também está sendo mastigado. Apenas um inimigo pode ser agarrado por vez.",
      "Carga Brutal Primitiva: Pode usar um movimento para atingir até três alvos em alcance Longe com um mesmo ataque.",
      "Código de Caçador Selvagem: Sempre escolhe como oponente o inimigo mais perigoso na cena. Caso seja ignorado, o Tecnossauro recebe Ganho em ataques contra ele."
    ],
    "tesouro": "Couro metálico e placas biotecnológicas.",
    "notas": [],
  },
  {
    "id": 26,
    "slug": "golem-de-guerra",
    "name": "Golem de Guerra",
    "points": 18,
    "power": "forte",
    "escala": "Sugoi",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 5,
    "habilidade": 1,
    "resistencia": 5,
    "pv": 30,
    "pericias": [
      "Luta",
      "Mística (descrito)"
    ],
    "vantagens": [
      "Forte",
      "Defesa Especial"
    ],
    "desvantagens": [
      "Sem Vida",
      "Lento"
    ],
    "poderes": [
      "Murro de além-Convergência: Uma vez a cada três turnos, o Golem concentra energia arcana na muqueta e desfere um golpe massivo: conta como um Ataque Especial (Potente, Titânico).",
      "Runas Elementais: Sempre que recebe um ataque com Magia e técnicas que a tenham como requisito, em vez de rolar defesa, o Golem recupera PV em quantidade igual aos PM gastos no ataque.",
      "Sem Vida MESMO: Você recebe Sem Vida, mas não pode ser consertado de jeito nenhum. Contudo, você recebe Regeneração 1, que funciona normalmente — exceto se for mantido sob alguma forma de dano contínuo."
    ],
    "tesouro": "Núcleo de Pedra Viva: Quando extraído com um teste de Mística (12), concede +5PM permanentes. Se falhar, ganha 5PM para uso único.",
    "notas": [
      "Atributos: `P5, H1, R5 (Estimados)`",
      "Recursos: `30 (Estimados) PV` (Desafios não possuem PM ou PA)"
    ],
  },
  {
    "id": 27,
    "slug": "cocatriz",
    "name": "Cocatriz",
    "points": 11,
    "power": "medio",
    "escala": "Ningen",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 2,
    "habilidade": 4,
    "resistencia": 3,
    "pv": 15,
    "pericias": [
      "Luta",
      "Sobrevivência"
    ],
    "vantagens": [
      "Ágil",
      "Sentido (Visão Aguçada)"
    ],
    "desvantagens": [
      "Inculto",
      "Monstruoso"
    ],
    "poderes": [
      "Bicada Petrificante: Sempre que faz um ataque, em vez de causar dano, pode forçar o alvo a fazer um teste de Resistência (9). Se falhar, fica petrificado (como a vantagem Paralisia) por 1D turnos. Se rolar falha crítica, a petrificação é permanente.",
      "Sentidos Galináceos: Por ter duas cabeças (galo e serpente) em extremos opostos do corpo, a Cocatriz sempre tem ganho em testes de Percepção e defesa contra ataques Perto.",
      "Terror de Bando: Se houver outra Cocatriz Perto, seus ataques têm Ganho."
    ],
    "tesouro": "Ovo de Cocatriz: Uma vez preparado, equivale a uma refeição gourmet (crítico automático em Resistência). Ou pode ser tacado no inimigo (vale um uso gratuito de Paralisia).",
    "notas": [],
  },
  {
    "id": 28,
    "slug": "asfixor",
    "name": "Asfixor",
    "points": 13,
    "power": "medio",
    "escala": "Ningen",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 3,
    "habilidade": 2,
    "resistencia": 4,
    "pv": 20,
    "pericias": [
      "Luta",
      "Percepção (mudar de cor)"
    ],
    "vantagens": [
      "Invisibilidade (camuflagem no teto)",
      "Sentido (Faro)"
    ],
    "desvantagens": [
      "Inculto",
      "Lento"
    ],
    "poderes": [
      "Muco Asqueroso: Qualquer personagem atacado ou agarrado pelo Asfixor fica lambuzado de muco fedorento, que não sai com banho. Adquire a desvantagem Aura 1 até o fim da aventura."
    ],
    "tesouro": "Membrana Sombria: Usada como capa, concede Ganho em testes para se esconder durante uma cena. Três usos antes de desmanchar.",
    "notas": [
      "Atributos: `P3, H2, R4 (Estimados)`",
      "Recursos: `20 (Estimados) PV` (Desafios não possuem PM ou PA)"
    ],
  },
  {
    "id": 29,
    "slug": "ursoruja",
    "name": "Ursoruja",
    "points": 14,
    "power": "medio",
    "escala": "Ningen",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 4,
    "habilidade": 2,
    "resistencia": 4,
    "pv": 20,
    "pericias": [
      "Luta",
      "Percepção"
    ],
    "vantagens": [
      "Forte",
      "Sentido (Visão Aguçada, Infravisão)"
    ],
    "desvantagens": [
      "Monstruoso",
      "Inculto"
    ],
    "poderes": [
      "Garra e Bico: Urso gigante com bico enorme de coruja. Seus olhos são capazes de encarar a alma. Ataques corporais ferozes."
    ],
    "tesouro": "Penas e garras valiosas.",
    "notas": [
      "Atributos: `P4, H2, R4 (Estimados)`",
      "Recursos: `20 (Estimados) PV` (Desafios não possuem PM ou PA)"
    ],
  },
  {
    "id": 30,
    "slug": "quimera",
    "name": "Quimera",
    "points": 16,
    "power": "medio",
    "escala": "Ningen",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 5,
    "habilidade": 3,
    "resistencia": 5,
    "pv": 25,
    "pericias": [
      "Luta",
      "Percepção"
    ],
    "vantagens": [
      "Forte",
      "Vigoroso"
    ],
    "desvantagens": [
      "Transtorno (qualquer)"
    ],
    "poderes": [
      "Tripla Ameaça: Pode fazer até três ataques Perto com uma única ação, contra alvos diferentes ou um mesmo alvo muito azarado.",
      "Baforada Surpresa: Uma vez no primeiro turno e depois a cada três turnos, pode fazer um Ataque Especial de qualquer tipo, escolhido pelo mestre.",
      "Fúria Costurada: Quando sofre dano, tem Ganho em seu próximo ataque.",
      "Mas Quimerd…: Quando encontrada, role 1D. Com um resultado 5 ou 6, a Quimera será uma versão Sugoi."
    ],
    "tesouro": "Couro Quimérico: Uma vez costurado como armadura, escudo ou chapéu (com teste de Arte 12 ou Sobrevivência 15), oferece Defesa Especial (Blindada) uma vez por cena.",
    "notas": [],
  },
  {
    "id": 31,
    "slug": "hidra",
    "name": "Hidra",
    "points": 20,
    "power": "forte",
    "escala": "Sugoi",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 4,
    "habilidade": 2,
    "resistencia": 5,
    "pv": 35,
    "pericias": [
      "Luta",
      "Percepção"
    ],
    "vantagens": [
      "Alcance 1",
      "Imune (Anfíbio, Doenças)",
      "Regeneração 2",
      "+Vida 1",
      "Vigorosa"
    ],
    "desvantagens": [
      "Monstruoso",
      "Diferente"
    ],
    "poderes": [
      "Múltiplas Mordidas: Uma Hidra sempre inicia o combate com 1D+1 cabeças, e faz um ataque por cabeça com uma ação, contra o mesmo alvo ou alvos diferentes.",
      "Baforada Peculiar: Em vez de fazer vários ataques, pode fazer um único Ataque Especial (Área, Distante). Esse ataque recebe Poder+1 para cada cabeça."
    ],
    "tesouro": "Sangue ou escamas de alta regeneração.",
    "notas": [],
  },
  {
    "id": 32,
    "slug": "beemorfo-parasitico",
    "name": "Beemorfo Parasítico",
    "points": 20,
    "power": "forte",
    "escala": "Sugoi",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 6,
    "habilidade": 4,
    "resistencia": 5,
    "pv": 45,
    "pericias": [
      "Luta",
      "Medicina",
      "Mística"
    ],
    "vantagens": [
      "+Vida 2"
    ],
    "desvantagens": [
      "Monstruoso"
    ],
    "poderes": [
      "Crescimento Acelerado: No fim de cada rodada, role 1D. Com 5 ou 6, adquire +5PV totais e +1 em todos os ataques. Cumulativos.",
      "Incorporação Progressiva: Sempre que derrota um alvo, absorve um pouco de sua aparência. Essa visão perturbadora causa Perda em quem tentar atacá-lo no próximo turno.",
      "Explosão de Forma Imatura: Quando reduzido à metade de seus PV, o Beemorfo sofre uma metamorfose súbita; recupera seus PV totais e todos os ataques contra ele sofrem Perda até o fim do próximo turno, por sua forma instável."
    ],
    "tesouro": "Resíduo Corporal Metamórfico: Item orgânico com propriedades mágicas. Pode ser consumido para ganhar 2 PA, mas o personagem apresenta 'sintomas' (adquire um Transtorno) pelo resto da sessão.",
    "notas": [],
  },
  {
    "id": 33,
    "slug": "teropode-t-rex-alossauro",
    "name": "Terópode (T-Rex / Alossauro)",
    "points": 17,
    "power": "forte",
    "escala": "Sugoi",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 6,
    "habilidade": 2,
    "resistencia": 4,
    "pv": 30,
    "pericias": [
      "Luta",
      "Percepção"
    ],
    "vantagens": [
      "Forte",
      "+Vida"
    ],
    "desvantagens": [
      "Diferente",
      "Inculto"
    ],
    "poderes": [
      "Mordida da Destruição: É considerada um Ataque Especial (Perigoso, Poderoso). Ele pode fazer esse ataque a cada 2 turnos.",
      "Mastigar e Engolir: O ataque Mordida da Destruição também conta como um Agarrão (Manual 3DeT Victory, p. 171). Um personagem agarrado, além de ficar imobilizado, também sofre 2D de dano por turno. Um personagem derrotado desta forma é engolido; só pode ser cuspido salvo com a derrota do T-Rex.",
      "Rugido Cinemático: Uma vez por cena, com um movimento, pode forçar os oponentes Perto a fazer um teste de Resistência (9). Quem falhar perde a próxima ação."
    ],
    "tesouro": "Dente de Titã: Um molar de T-Rex. Concede Ganho em testes de Influência para intimidar, uma vez por cena. Em cada uso, role 1D: caindo 1, atrai outro T-Rex em resposta.",
    "notas": [],
  },
  {
    "id": 34,
    "slug": "ceratopsideo",
    "name": "Ceratopsídeo",
    "points": 16,
    "power": "medio",
    "escala": "Sugoi",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 5,
    "habilidade": 1,
    "resistencia": 5,
    "pv": 45,
    "pericias": [
      "Luta",
      "Esporte"
    ],
    "vantagens": [
      "+Vida 2",
      "Vigoroso"
    ],
    "desvantagens": [
      "Inculto",
      "Diferente"
    ],
    "poderes": [
      "Investida Triangular: Se usar um movimento antes de atacar, pode realizar um Ataque Especial (Investida) com Ganho.",
      "Estouro Territorial: Pode usar um movimento para atingir até três alvos até Longe com um mesmo ataque."
    ],
    "tesouro": "Escudo de Osso: Oferece Ganho em defesa uma vez por cena.",
    "notas": [],
  },
  {
    "id": 35,
    "slug": "sauropode-colosso-primitivo",
    "name": "Saurópode (Colosso Primitivo)",
    "points": 16,
    "power": "medio",
    "escala": "Kiodai",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 4,
    "habilidade": 2,
    "resistencia": 5,
    "pv": 45,
    "pericias": [
      "Percepção"
    ],
    "vantagens": [
      "+Vida 3",
      "Vigoroso"
    ],
    "desvantagens": [
      "Diferente",
      "Inculto"
    ],
    "poderes": [
      "Chicote Caudal: Pode golpear todos os inimigos Perto com um único ataque de cauda. Este ataque sempre tem Ganho.",
      "Movimento Descomunal: Sempre que realiza um movimento, todos os personagens de escala inferior (ou seja, praticamente todo mundo) que estejam Perto fazem um teste de Habilidade (9) para não cair.",
      "Presença Imensa: Testes para perceber qualquer outra criatura (de escala inferior) na cena sofrem Perda."
    ],
    "tesouro": "Vértebra da Terra Antiga: Osso enorme que ainda pulsa com energia tectônica. Chocado contra o chão, reproduz o efeito do Movimento Descomunal uma única vez. Então esfarela.",
    "notas": [],
  },
  {
    "id": 36,
    "slug": "boitata-das-brasas",
    "name": "Boitatá das Brasas",
    "points": 11,
    "power": "medio",
    "escala": "Ningen",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 4,
    "habilidade": 3,
    "resistencia": 2,
    "pv": 20,
    "pericias": [
      "Luta",
      "Percepção"
    ],
    "vantagens": [
      "Alcance 1",
      "Ligeiro (descritivo)"
    ],
    "desvantagens": [
      "Fraqueza (Água)",
      "Inculto"
    ],
    "poderes": [
      "Chicote de Escamas Flamejantes: Qualquer alvo que recebe dano de seus ataques pega fogo, sofrendo +1D de dano no turno seguinte do Boitatá.",
      "Olho da Combustão Interior: Uma vez por cena, conjura o terceiro olho de fogo acima da cabeça. Todos os inimigos até Longe fazem um teste de Resistência (12) para não sofrer Perda em seu próximo turno, por ofuscamento e medo."
    ],
    "tesouro": "Ovo Elemental do Fogo: Caso seja cuidado e chocado entre sessões, o personagem ganha um Ajudante Elemental do Fogo.",
    "notas": [],
  },
  {
    "id": 37,
    "slug": "sereia-da-folha-lucida",
    "name": "Sereia da Folha Lúcida",
    "points": 13,
    "power": "medio",
    "escala": "Ningen",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 3,
    "habilidade": 3,
    "resistencia": 5,
    "pv": 25,
    "pericias": [
      "Mística",
      "Medicina"
    ],
    "vantagens": [
      "Imune (Anfíbio)",
      "Paralisia (olhar)"
    ],
    "desvantagens": [
      "Inculto",
      "Dependência (Água)"
    ],
    "poderes": [
      "Braços de Cabelo Fluido: Com uma ação, pode fazer dois ataques contra alvos Perto. Se feitos contra o mesmo alvo, este sofre Perda na defesa.",
      "Chuva Curativa da Calmaria: Uma vez por cena, pode curar todos os PV em si mesma ou uma criatura Perto. O alvo também brilha com luz azulada, causando Perda em ataques contra ele durante 1 rodada.",
      "Reflexo de Lago Mágico: Sempre que rolar um crítico em defesa, será uma Defesa Especial (Reflexão). Se rolar dois ou mais críticos, também será Titânica."
    ],
    "tesouro": "Concha de Memória Líquida: Uma vez por sessão, permite lembrar um detalhe esquecido que oferece um crítico automático em um teste de perícia. Mas depois o usuário esquece um fato inútil aleatório.",
    "notas": [],
  },
  {
    "id": 38,
    "slug": "grunk-guerreiro-perpetuo-grunt",
    "name": "Grunk (Guerreiro Perpétuo / Grunt)",
    "points": 5,
    "power": "fraco",
    "escala": "Ningen",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 1,
    "habilidade": 1,
    "resistencia": 1,
    "pv": 5,
    "pericias": [
      "Luta"
    ],
    "vantagens": [],
    "desvantagens": [
      "Monstruoso",
      "Inculto"
    ],
    "poderes": [
      "Ataque Genérico com Clava Genérica: Ataque simples. Pode repetir indefinidamente. Só esse.",
      "Fúria de Manual: Caso esteja perto da derrota (evento raro; quase todas as vezes, é derrotado direto), grita “GRUNK NÃO ACABA!” e ganha +1 em dano até o fim da cena. Mesmo que morra em seguida."
    ],
    "tesouro": "Manual de Grito de Guerra de Grunk — pergaminho com 2D versões de “GRUNK VAI QUEBRAR”. Cada versão dá Ganho em um teste de Influência contra outros orcs, se gritado bem alto.",
    "notas": [],
  },
  {
    "id": 39,
    "slug": "cobra-do-tatame",
    "name": "Cobra do Tatame",
    "points": 22,
    "power": "forte",
    "escala": "Sugoi",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 6,
    "habilidade": 3,
    "resistencia": 5,
    "pv": 25,
    "pericias": [
      "Luta",
      "Manha",
      "Esporte"
    ],
    "vantagens": [
      "Forte",
      "Ligeiro",
      "Acumulador"
    ],
    "desvantagens": [
      "Má Fama",
      "Infame"
    ],
    "poderes": [
      "Ali Onde Dói: O Cobra do Tatame sempre tem Ganho em ataques contra oponentes já feridos, com PV abaixo do total.",
      "Ataque Além do Apito: Sempre que o alvo rola 1 em defesa, o Cobra ganha um ataque extra imediato contra ele. “Não ouvi o gongo, que pena!”",
      "Matança para a Plateia: Ao derrotar um alvo, todos os outros inimigos na cena testam Resistência (12) ou ficam com medo e sofrem Perda na próxima ação."
    ],
    "tesouro": "Faixa do Lutador Desonrado: Quem equipa esta faixa ganha, uma vez por sessão, sucesso automático em um único teste de Manha (meta até 12).",
    "notas": [
      "Atributos: `P6, H3, R5 (Estimados com base na pontuação e papel)`",
      "Recursos: `25 (Estimados) PV` (Desafios não possuem PM ou PA)"
    ],
  },
  {
    "id": 40,
    "slug": "terrorpassaro",
    "name": "Terrorpássaro",
    "points": 14,
    "power": "medio",
    "escala": "Ningen",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 3,
    "habilidade": 3,
    "resistencia": 2,
    "pv": 10,
    "pericias": [
      "Luta",
      "Percepção (descrito)"
    ],
    "vantagens": [
      "Aceleração",
      "Ágil"
    ],
    "desvantagens": [
      "Inculto",
      "Diferente"
    ],
    "poderes": [
      "Corrida que Divide o Ar: Com um ação completa, pode realizar um Ataque Especial (Investida). Este ataque sempre tem Ganho.",
      "Olhar de Predador Vertical: Testes para se esconder do Terrorpássaro sofrem Perda. Ele sempre vê primeiro. E nunca esquece um rosto."
    ],
    "tesouro": "Pena de Caçada Primordial: Presa à roupa, confere Ganho em um teste de Percepção por sessão. Mas o usuário passa a emitir gritinhos guturais ao farejar pistas.",
    "notas": [
      "Atributos: `P3, H3, R2 (Estimados)`",
      "Recursos: `10 (Estimados) PV` (Desafios não possuem PM ou PA)"
    ],
  },
  {
    "id": 41,
    "slug": "tigre-dentes-de-sabre",
    "name": "Tigre-Dentes-de-Sabre",
    "points": 15,
    "power": "medio",
    "escala": "Ningen",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 4,
    "habilidade": 4,
    "resistencia": 3,
    "pv": 15,
    "pericias": [
      "Luta",
      "Sobrevivência"
    ],
    "vantagens": [
      "Ágil",
      "Sentido (Audição Aguçada)"
    ],
    "desvantagens": [
      "Inculto",
      "Monstruoso"
    ],
    "poderes": [
      "Salto Silencioso de Caçador: Pode iniciar o combate Perto de qualquer inimigo na cena. Ele também tem Ganho no primeiro ataque contra esse alvo.",
      "Mordida Quebra-História: Seu ataque ignora Ganho em defesa e qualquer Defesa Especial.",
      "Revanche da Era Perdida: Quando ferido, tem Ganho em ataques contra qualquer alvo que tenha lhe causado dano."
    ],
    "tesouro": "Presas de Memória Selvagem: Oferece Ganho em um teste de Luta por cena. Só funciona se o usuário rugir com sinceridade ancestral.",
    "notas": [],
  },
  {
    "id": 42,
    "slug": "mamute-lanoso",
    "name": "Mamute Lanoso",
    "points": 19,
    "power": "forte",
    "escala": "Sugoi",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 5,
    "habilidade": 2,
    "resistencia": 5,
    "pv": 45,
    "pericias": [
      "Luta",
      "Sobrevivência"
    ],
    "vantagens": [
      "Imune (Resiliente)",
      "Resoluto",
      "+Vida 2",
      "Vigoroso"
    ],
    "desvantagens": [
      "Diferente",
      "Inculto"
    ],
    "poderes": [
      "Investida de Geada: Com uma ação completa, pode fazer um Ataque Especial (Investida). Sempre tem Ganho neste ataque.",
      "Tromba de Avalanche: Para cada crítico que consegue ao atacar, o ataque também atinge outro alvo Perto.",
      "Pelagem de Era Glacial: Resistente a dano por frio (Manual 3DeT Victory, p. 174). Mas vulnerável a dano por fogo (afinal, não é burro)."
    ],
    "tesouro": "Presas Ressonantes do Inverno Perpétuo: Ganho em testes de Percepção para detectar criaturas até Longe. Emitem um leve “glon-glon” ao fazê-lo.",
    "notas": [],
  },
  {
    "id": 43,
    "slug": "escamador",
    "name": "Escamador",
    "points": 20,
    "power": "forte",
    "escala": "Ningen",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 7,
    "habilidade": 2,
    "resistencia": 4,
    "pv": 20,
    "pericias": [
      "Luta",
      "Manha"
    ],
    "vantagens": [
      "Ágil",
      "Forte",
      "Vigoroso"
    ],
    "desvantagens": [
      "Monstruoso",
      "Inculto"
    ],
    "poderes": [
      "Bote: O escamador considera H4 e acertos críticos com 5 ou 6 em testes de Iniciativa.",
      "Rebote: Sempre que recebe dano, o escamador revida com um golpe da cauda contra algum alvo que esteja Perto (mesmo que o dano seja causado por outro defensor). Rebotes não contam como ação.",
      "Giro da Morte: Sempre que conseguir um crítico usando Rebote, o alvo considera Perda na defesa contra esse ataque."
    ],
    "tesouro": "Bolsa de Couro de Escamador: Uma bolsa azul e amarela horrível, mas que dobra a quantidade de itens garantidos pela vantagem Inventário. Ela também fica invisível quando colocada de lado por muito tempo.",
    "notas": [],
  },
  {
    "id": 44,
    "slug": "minhocranios",
    "name": "Minhocrânios",
    "points": 7,
    "power": "fraco",
    "escala": "Ningen",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 2,
    "habilidade": 2,
    "resistencia": 1,
    "pv": 5,
    "pericias": [
      "Luta",
      "Manha"
    ],
    "vantagens": [],
    "desvantagens": [
      "Inculto",
      "Monstruoso"
    ],
    "poderes": [
      "Emboscada Subterrânea: Em mapas apropriados (túneis, cavernas, masmorras), minhocrânios atacam a partir dos buracos onde se escondem. Sempre fazem seu teste de iniciativa com Ganho.",
      "Enrolação Pegajosa: Um minhocrânio pode se enrolar em um alvo para imobilizá-lo, fazendo um ataque com a manobra agarrão (Manual 3DeT Victory, p. 171). Ele sempre tem Ganho neste ataque. Enquanto agarra, não pode realizar outras ações: o objetivo é manter o alvo vulnerável contra ataques dos outros minhocrânios."
    ],
    "tesouro": "Nenhum. Minhocrânios só carregam carne podre, dentes tortos, pedaços de osso e a certeza de que você vai precisar de curativos depois.",
    "notas": [],
  },
  {
    "id": 45,
    "slug": "primevore",
    "name": "Primevore",
    "points": 20,
    "power": "forte",
    "escala": "Sugoi",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 7,
    "habilidade": 2,
    "resistencia": 5,
    "pv": 45,
    "pericias": [
      "Luta",
      "Sobrevivência (espreitar)"
    ],
    "vantagens": [
      "Alcance 1",
      "Forte"
    ],
    "desvantagens": [
      "Inculto",
      "Monstruoso"
    ],
    "poderes": [
      "Tentáculos: Com uma única ação, o Primevore pode atacar qualquer número de alvos na cena, até Longe. Ou pode fazer quatro ataques, contra um mesmo alvo ou alvos diferentes, como achar melhor. Para estes ataques, ele tem Poder 3.",
      "Bocarra Trituradora: Ataque principal do Primevore (com Poder 7) é considerado um Ataque Especial (Perigoso, Poderoso). Ele pode fazer esse ataque a cada 2 turnos.",
      "Mastigar e Engolir: O ataque Bocarra Trituradora também conta como um agarrão (Manual 3DeT Victory, p. 171). Um personagem agarrado, além de ficar imobilizado, também sofre 2D de dano por turno. Um personagem derrotado desta forma é engolido; só pode ser salvo com a morte do Primevore.",
      "Volta Aqui!: Primevore é voraz, mas também antigo e inteligente. Caso seus PV sejam reduzidos até perto da derrota, ele usa um turno para se recolher e realizar uma fuga (Manual 3DeT Victory, p. 173)."
    ],
    "tesouro": "As entranhas do Primevore costumam conter itens de vítimas anteriores. Faça um teste de Percepção ou Sobrevivência (9). Em caso de sucesso, acha 1D itens incomuns. Para cada crítico, acha também 1 item raro. Tome um bom banho depois.",
    "notas": [
      "Atributos: `P7 (Bocarra), P3 (Tentáculos), H2, R5 (Estimados)`",
      "Recursos: `45 (Estimados) PV` (Desafios não possuem PM ou PA)"
    ],
    "poder_alt": 3,
  },
  {
    "id": 46,
    "slug": "corrompidos",
    "name": "@Corrompidos$",
    "points": 15,
    "power": "medio",
    "escala": "Ningen",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 4,
    "habilidade": 4,
    "resistencia": 4,
    "pv": 20,
    "pericias": [
      "Luta",
      "Máquinas",
      "Manha"
    ],
    "vantagens": [],
    "desvantagens": [
      "Diferente"
    ],
    "poderes": [
      "Todos Sangram, Todos Matam: Quando encontrados, os @Corrompidos$ são formados por 1D+2 membros, compartilhando os mesmos Pontos de Vida — como a desvantagem Elo Vital (Manual 3DeT Victory, p. 68). Cada membro faz um ataque por rodada.",
      "Ataque de Reflexo Fantasma: Quando um membro é atacado, o agressor recebe um contra-ataque imediato como reação de outro membro. Os @Corrompidos$ podem fazer isso uma vez por turno.",
      "Sincronização Bugada: Quando dois @Corrompidos$ fazem ataques bem-sucedidos, aqueles que ainda não atacaram neste turno recebem Ganho no próximo ataque.",
      "Comando Remoto: Uma vez por cena, os @Corrompidos$ podem tentar controlar um alvo, decidindo sua ação e movimento. Requer teste de Resistência (12) para evitar."
    ],
    "tesouro": "Identidade Desvinculada: Chip ou amuleto corrompido. Permite ao portador usar uma vantagem de um aliado durante 1 turno. Tem 1D+2 cargas.",
    "notas": [],
  },
  {
    "id": 47,
    "slug": "crashmutante-de-buffer",
    "name": "Crashmutante de Buffer",
    "points": 15,
    "power": "medio",
    "escala": "Ningen",
    "category": "ferozes",
    "category_label": "Ferozes e Furiosos",
    "origem": "Ferozes e Furiosos",
    "poder": 3,
    "habilidade": 4,
    "resistencia": 3,
    "pv": 15,
    "pericias": [
      "Luta",
      "Máquinas"
    ],
    "vantagens": [],
    "desvantagens": [
      "Diferente"
    ],
    "poderes": [
      "Frame Fantasma: Uma vez por turno, ao receber um ataque bem-sucedido, o Crashmutante pode voltar para a posição anterior, desfazendo o ataque.",
      "Buffer Saturado: Caso seus PV sejam reduzidos à metade, libera uma onda de ruído. Todos os personagens Perto fazem um teste de Resistência (9), quem falhar perde sua próxima ação (lag ou distorção sensorial).",
      "Megacrash: Quando encontrado, role 1D. Com um resultado 5 ou 6, a criatura será uma versão Sugoi."
    ],
    "tesouro": "Linguagem Esquecida: Um núcleo residual de instruções incoerentes. Faça um teste de Máquinas, Percepção ou Sobrevivência (9). Em caso de sucesso, adquire 1D Pontos de Ação que todos no grupo podem usar quando quiserem. Para cada crítico, acha +2PA extras. O item funciona uma única vez.",
    "notas": [
      "Atributos: `P3, H4, R3 (Estimados)`",
      "Recursos: `15 (Estimados) PV` (Desafios não possuem PM ou PA)"
    ],
  },
]

def filter_bestiary(
    *,
    power: str | None = None,
    category: str | None = None,
    escala: str | None = None,
    query: str | None = None,
    name: str | None = None,
) -> list[dict[str, Any]]:
    needle = (query or "").strip().lower()
    wanted = (name or "").strip().lower()
    out: list[dict[str, Any]] = []
    for entry in BESTIARY:
        if wanted and wanted not in {entry["name"].lower(), entry["slug"]}:
            continue
        if power and power not in {"", "todos"} and entry["power"] != power:
            continue
        if category and category not in {"", "todos"} and entry["category"] != category:
            continue
        if escala and escala not in {"", "todas"} and entry["escala"] != escala:
            continue
        if needle:
            blob = " ".join(
                [
                    entry["name"],
                    entry["origem"],
                    entry["category_label"],
                    entry["escala"],
                    " ".join(entry["pericias"]),
                    " ".join(entry["vantagens"]),
                    " ".join(entry["poderes"]),
                ]
            ).lower()
            if needle not in blob:
                continue
        out.append(entry)
    return out


def find_bestiary(name_or_slug: str) -> dict[str, Any] | None:
    key = name_or_slug.strip().lower()
    for entry in BESTIARY:
        if entry["slug"] == key or entry["name"].lower() == key:
            return entry
    return None
