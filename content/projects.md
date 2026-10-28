+++
title = "Projects"
tagline = "Projects"
lede = "Fourteen years of things I've built: open source, client products, and community work."
+++

Most of it is Python and Django backends; lately it's AI agents. These days I lead engineering on [Rosey](https://meetrosey.ai), [Fueled](https://fueled.com)'s AI-native delivery platform. [Now](/now/) has the details.

This is a selection. Smaller things live on [GitHub](https://github.com/theskumar), and some client work isn't public.

## Open source

2014–now
: **[python-dotenv](https://github.com/theskumar/python-dotenv)** — loads environment variables from `.env` files. I wrote it after credentials leaked from a codebase where I worked: secrets belong in the environment, not in git. It borrowed ideas from libraries around at the time, but I wanted something more focused that does one thing well, the Unix way. I think that's why it caught on: one `load_dotenv()` call and a file format with few surprises. It now gets about 580 million downloads a month, and libraries like pydantic-settings and uvicorn depend on it. I maintain it with Bertrand Bonnefoy-Claudet.

2013–2016
: **[cookiecutter-django](https://github.com/cookiecutter/cookiecutter-django)** — a production-ready template for new Django projects, started by Daniel Roy Greenfeld. I contributed heavily and helped maintain it, reviewing and merging pull requests.

2014–2024
: **[django-init](https://github.com/Fueled/django-init)** — a simpler take on cookiecutter-django for Fueled's own projects. I started it in 2014 and wrote most of it.

2022–2025
: **[hypha](https://github.com/HyphaApp/hypha)** — the Open Technology Fund's platform for open calls, grant applications and reviews. I was a core contributor through OTF, and later built [Urgent Action Fund](https://urgentactionfund.org/)'s grants platform on a private fork of it.

2026
: **[Pi Pocket Blackhole](https://github.com/theskumar/pi-pocket-blackhole)** — compacts long agent sessions in [Pi Pocket](https://github.com/TannerMidd/pi-pocket) without a model call. It came out of my research on agent memory. Summaries use [pi-blackhole](https://github.com/k0valik/pi-blackhole)'s deterministic extraction, and a recall tool reads the original messages back from refs in the summary.

2015
: **[python-usernames](https://github.com/theskumar/python-usernames)** — checks that usernames are URL-safe and not reserved or abusive.

2015–2016
: **[junction](https://github.com/pythonindia/junction)** — proposal management for PyCon India and PyDelhi. I was one of its contributors. The project is closed now.

## Client work

2026
: **C. S. Lewis (unreleased)** — a CMS and an interactive mobile app built around his writing, not an e-book reader. The CMS, on Wagtail, links his works through the themes they share. I was technical lead for backend and infrastructure. It launches soon.

2026
: **[South Pole](https://www.southpole.com/)** — AI for South Pole's Quality Management Framework. It answers registry questionnaires from carbon-credit project documents (Verra, Gold Standard) with page-level citations, then drafts reports from those answers. Each answer is checked for missing citations, conflicting sources and confidence, and evals measure output quality. I did the research and architecture, and built the working concepts.

2026
: **[Christianity Today](https://www.christianitytoday.com/)** — a backend for their new mobile app that turns WordPress content into clean, fast APIs. I built it.

2024–now
: **[2NDFLOOR](https://www.2ndfloor.org)** — an anonymous support community for youth mental health. I rebuilt the backend and APIs for their Flutter app, and community engagement rose 6× after launch.

2024–2025
: **[IrisMD](https://www.irismd.com/)** — an AI-assisted medical scribe that turns live patient conversations into EHR notes. I started the codebase and researched transcription. Self-hosted Whisper cost more and transcribed worse than OpenAI's API, so we used OpenAI under a HIPAA business associate agreement.

2023–2026
: **[The Motley Fool](https://www.fool.com/)** — their premium subscription platform: a Vue-to-Next.js migration, a shared design system, and a GraphQL layer over legacy, distributed backends. I worked on it as a contract engineer in their team.

2022–2023
: **[NationsBenefits](https://www.nationsbenefits.com/)** — the experience API behind their member apps: a GraphQL layer with its infrastructure, schema, developer docs and mock servers. I started it and set up its architecture.

2022
: **[Victoria's Secret Community](https://fueled.com/work/victorias-secret/)** — a real-time community feed inside their mobile app, built for a mass-market retail audience. I did the initial architecture and solution design.

2019–2024
: **[Tony Robbins](https://www.tonyrobbins.com/)** — two apps. I built the backend for [Breakthrough](https://www.tonyrobbins.com/breakthrough-app), which streams video and audio to a large audience, then led the backend for the [RPM Planner](https://rpmplanner.com/), a web and iOS planner with AI voice coaching. Another team built the voice coach, and I worked on integrating it.

2016–2018
: **[Spoken Tutorials, IIT Bombay](https://github.com/Spoken-tutorial/spoken-website)** — the open-source Django platform for the Government of India's tech literacy initiative. I started as tech lead, and in later phases managed their engineers as technical program manager.

2015–2017
: **[Apple](https://fueled.com/work/apple/)** — Junction, a learning platform for Apple's EMEA carrier retail staff: a gamification engine and a multilingual, multi-region CMS behind an Android training app. I was one of its two main backend engineers.

Also
: a mobile app spike for Comoto (RevZilla, Cycle Gear, J&P Cycles, 2026), the CRM data layer for [Goosehead Insurance](https://www.goosehead.com)'s app (2025), game backends for [EverFi](https://everfi.com) (2022), a patient portal for [Beacon Health System](https://www.beaconhealthsystem.org/) (2021), backends for [Alpas Wellness Centers](https://alpaswellnesscenters.org/) and [Omstars](https://omstars.com/) (2017), and Raw Mango.

## Community

2014–2018
: **[PyDelhi](https://pydelhi.org)** — the Delhi Python meetup. I revived it and ran it for four years.

2015
: **[Two Scoops of Django](https://www.feldroy.com/products/two-scoops-of-django-3-x)** — I was a technical reviewer for the 1.8 edition, written by Daniel and Audrey Roy Greenfeld.

## Personal

These are my own setup, public so others can borrow from them. I don't maintain them for other people.

2026–now
: **[Agent Stuff](https://github.com/theskumar/agent-stuff)** — my extensions, skills and prompts for Pi and Claude Code, including review and handoff workflows. Sources for adapted pieces are credited in the repository.

2013–now
: **[Dotfiles](https://github.com/theskumar/dotfiles)** — my working environment, including the [shell-startup audit](/articles/2026/05/how-i-optimized-my-zsh-startup-time/).
