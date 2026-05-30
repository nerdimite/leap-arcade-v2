"""Captured-style Wikimedia HTML fragments for wiki API tests (no live network).

Optimal-path pages from `leap/seeds/data/wiki.json` are represented with minimal
markup so rewriter policy tests can run without hitting the REST API.
"""

# --- Shared / Round 1–3 (start: Biology) ---
BIOLOGY_HTML = """<section id="bodyContent"><p>Biology</p>
<a href="/wiki/Biology_in_fiction">fiction</a>
<a href="/wiki/DNA">dna</a>
</section>"""

BIOLOGY_IN_FICTION_HTML = """<section id="bodyContent"><p>Fiction</p>
<a href="/wiki/Intelligent_machine">intel</a>
<a href="https://evil.example/leak">bad</a>
<a href="/wiki/Some_page#cite_note-z">cite</a>
</section>"""

# Redirecting title lands as Artificial intelligence (one navigation step).
INTELLIGENT_MACHINE_HTML = """<section id="bodyContent"><p>AI topic</p>
<a href="/wiki/Attention_(machine_learning)">target r1</a>
<a href="/wiki/Word_embedding">target r2</a>
</section>"""

ATTENTION_ML_HTML = (
    """<section id="bodyContent"><p>Attention (machine learning) goal</p></section>"""
)

WORD_EMBEDDING_HTML = """<section id="bodyContent"><p>Word embedding goal</p></section>"""

DNA_HTML = """<section id="bodyContent"><p>DNA</p>
<a href="/wiki/Machine_learning">ml</a></section>"""

MACHINE_LEARNING_HTML = """<section id="bodyContent"><p>ML</p>
<a href="/wiki/Autoencoder">ae</a></section>"""

AUTOENCODER_HTML = """<section id="bodyContent"><p>Autoencoder goal</p></section>"""

# --- Rounds 4–5 (start: Computer) ---
COMPUTER_HTML = """<section id="bodyContent"><p>Computer</p>
<a href="/wiki/ARM_architecture">arm</a>
<a href="/wiki/BIOS">bios</a>
</section>"""

ARM_ARCHITECTURE_HTML = """<section id="bodyContent"><p>ARM family</p>
<a href="/wiki/FreeBSD">bsd</a></section>"""

FREEBSD_HTML = """<section id="bodyContent"><p>FreeBSD</p>
<a href="/wiki/Amazon_Elastic_Compute_Cloud">ec2</a></section>"""

AMAZON_EC2_HTML = """<section id="bodyContent"><p>Amazon EC2 goal</p></section>"""

BIOS_HTML = """<section id="bodyContent"><p>BIOS</p>
<a href="/wiki/API">api</a></section>"""

API_HTML = """<section id="bodyContent"><p>API</p>
<a href="/wiki/Microservices">ms</a></section>"""

MICROSERVICES_HTML = """<section id="bodyContent"><p>Microservices goal</p></section>"""

# All fragments exercised by rewriter / happy-path fixture coverage
SEED_HTML_FIXTURES: dict[str, str] = {
    "biology": BIOLOGY_HTML,
    "biology_in_fiction": BIOLOGY_IN_FICTION_HTML,
    "intelligent_machine": INTELLIGENT_MACHINE_HTML,
    "attention_ml": ATTENTION_ML_HTML,
    "word_embedding": WORD_EMBEDDING_HTML,
    "dna": DNA_HTML,
    "machine_learning": MACHINE_LEARNING_HTML,
    "autoencoder": AUTOENCODER_HTML,
    "computer": COMPUTER_HTML,
    "arm_architecture": ARM_ARCHITECTURE_HTML,
    "freebsd": FREEBSD_HTML,
    "amazon_ec2": AMAZON_EC2_HTML,
    "bios": BIOS_HTML,
    "api": API_HTML,
    "microservices": MICROSERVICES_HTML,
}
