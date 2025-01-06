\documentclass[10pt, letterpaper]{article}

% Packages:
\usepackage[
ignoreheadfoot, % set margins without considering header and footer
top=2 cm, % separation between body and page edge from the top
bottom=2 cm, % separation between body and page edge from the bottom
left=2 cm, % separation between body and page edge from the left
right=2 cm, % separation between body and page edge from the right
footskip=1.0 cm, % separation between body and footer
]{geometry} % for adjusting page geometry
\usepackage{titlesec} % for customizing section titles
\usepackage{tabularx} % for making tables with fixed width columns
\usepackage{array} % tabularx requires this
\usepackage[dvipsnames]{xcolor} % for coloring text
\definecolor{primaryColor}{RGB}{0, 79, 144} % define primary color
\usepackage{enumitem} % for customizing lists
\usepackage{fontawesome5} % for using icons
\usepackage{amsmath} % for math
\usepackage[
pdftitle={Shubham Chauhan's CV},
pdfauthor={Shubham Chauhan},
pdfcreator={LaTeX with RenderCV},
colorlinks=true,
urlcolor=primaryColor
]{hyperref} % for links, metadata and bookmarks
\usepackage[pscoord]{eso-pic} % for floating text on the page
\usepackage{calc} % for calculating lengths
\usepackage{bookmark} % for bookmarks
\usepackage{lastpage} % for getting the total number of pages
\usepackage{changepage} % for one column entries (adjustwidth environment)
\usepackage{paracol} % for two and three column entries
\usepackage{ifthen} % for conditional statements
\usepackage{needspace} % for avoiding page break right after the section title
\usepackage{iftex} % check if engine is pdflatex, xetex or luatex

% Ensure that generated pdf is machine readable/ATS parsable:
\ifPDFTeX
\input{glyphtounicode}
\pdfgentounicode=1
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\fi

% Some settings:
\AtBeginEnvironment{adjustwidth}{\partopsep0pt} % remove space before adjustwidth environment
\pagestyle{empty} % no header or footer
\setcounter{secnumdepth}{0} % no section numbering
\setlength{\parindent}{0pt} % no indentation
\setlength{\topskip}{0pt} % no top skip
\setlength{\columnsep}{0cm} % set column separation
\makeatletter
\let\ps@customFooterStyle\ps@plain % Copy the plain style to customFooterStyle
\patchcmd{\ps@customFooterStyle}{\thepage}{
\color{gray}\textit{\small Shubham Chauhan - Page \thepage{} of \pageref\*{LastPage}}
}{}{} % replace number by desired string
\makeatother
\pagestyle{customFooterStyle}

% Slightly tighter section spacing to save vertical space
\titleformat{\section}{\needspace{4\baselineskip}\bfseries\large}{}{0pt}{}[\vspace{1pt}\titlerule]
\titlespacing{\section}{
-1pt
}{
0.18 cm % reduced top space
}{
0.12 cm % reduced bottom space
} % section title spacing

\renewcommand\labelitemi{$\circ$} % custom bullet points

% Slightly denser list spacing
\newenvironment{highlights}{
\begin{itemize}[
topsep=0.05 cm,
parsep=0.05 cm,
partopsep=0pt,
itemsep=0pt,
leftmargin=0.3cm
]
}{
\end{itemize}
} % new environment for highlights

\newenvironment{highlightsforbulletentries}{
\begin{itemize}[
topsep=0.05 cm,
parsep=0.05 cm,
partopsep=0pt,
itemsep=0pt,
leftmargin=10pt
]
}{
\end{itemize}
} % new environment for highlights for bullet entries

\newenvironment{onecolentry}{
\begin{adjustwidth}{
0.2 cm + 0.00001 cm
}{
0.2 cm + 0.00001 cm
}
}{
\end{adjustwidth}
} % new environment for one column entries

\newenvironment{twocolentry}[2][]{
\onecolentry
\def\secondColumn{#2}
\setcolumnwidth{\fill, 4.5 cm}
\begin{paracol}{2}
}{
\switchcolumn \raggedleft \secondColumn
\end{paracol}
\endonecolentry
} % new environment for two column entries

\newenvironment{header}{
\setlength{\topsep}{0pt}\par\kern\topsep\centering\linespread{1.4}
}{
\par\kern\topsep
} % new environment for the header (slightly tighter linespread)

\newcommand{\placelastupdatedtext}{% \placetextbox{<horizontal pos>}{<vertical pos>}{<stuff>}
\AddToShipoutPictureFG\*{% Add <stuff> to current page foreground
\put(
\LenToUnit{\paperwidth-2 cm-0.2 cm+0.05cm},
\LenToUnit{\paperheight-1.0 cm}
){\vtop{{\null}\makebox[0pt][c]{
        \small\color{gray}\textit{}\hspace{\widthof{}}
}}}%
}%
}%

% save the original href command in a new command:
\let\hrefWithoutArrow\href

% new command for external links:
\renewcommand{\href}[2]{\hrefWithoutArrow{#1}{\ifthenelse{\equal{#2}{}}{ }{#2 }\raisebox{.15ex}{\footnotesize \faExternalLink\*}}}

\begin{document}
% Slightly reduce global body font to fit more content while keeping readability
\small

    \newcommand{\AND}{\unskip
        \cleaders\copy\ANDbox\hskip\wd\ANDbox
        \ignorespaces
    }
    \newsavebox\ANDbox
    \sbox\ANDbox{}

    \placelastupdatedtext
    \begin{header}
        % header font reduced a bit to save space
        \textbf{\fontsize{20 pt}{20 pt}\selectfont Shubham Chauhan}

        \vspace{0.22 cm}

        \normalsize
        \mbox{{\color{black}\footnotesize\faMapMarker*}\hspace*{0.13cm} Ghaziabad, U.P., India}%
        \kern 0.20 cm%
        \AND%
        \kern 0.20 cm%
        \mbox{\hrefWithoutArrow{mailto: shubham.flag@gmail.com}{\color{black}{\footnotesize\faEnvelope[regular]}\hspace*{0.13cm} shubham.flag@gmail.com}}%
        \kern 0.20 cm%
        \AND%
        \kern 0.20 cm%
        \mbox{\hrefWithoutArrow{tel:+91-8954731184}{\color{black}{\footnotesize\faPhone*}\hspace*{0.13cm}+91-8954731184}}%
        \kern 0.20 cm%
        \AND%
        \kern 0.20 cm%
        \mbox{\hrefWithoutArrow{https://www.linkedin.com/in/shubham-chauhan-673b402b1/}{\color{black}{\footnotesize\faLinkedinIn}\hspace*{0.13cm} LinkedIn}}%
        \kern 0.20 cm%
        \AND%
        \kern 0.20 cm%
        \mbox{\hrefWithoutArrow{https://github.com/Demiserular}{\color{black}{\footnotesize\faGithub}\hspace*{0.13cm} GitHub}}%
    \end{header}

    \vspace{0.12 cm}

    \section{Technical Projects}
        \begin{twocolentry}{\textit{\href{https://github.com/Demiserular/CRUCIBLE-EXCHANGE}{GitHub}}}
            \textbf{Crucible Exchange: High-Performance FIX Protocol Trading System}
        \end{twocolentry}
        \vspace{0.06cm}
        \begin{onecolentry}
            \begin{highlights}
                \item Engineered full-stack mock exchange implementing FIX 4.2 protocol — real-time order matching (5000+ orders/sec, sub-100ms latency), WebSocket market data streaming, REST API and live trading dashboard.
                \item Built Python multi-threaded server with raw socket programming, O(n log n) price-time priority matching algorithm, SQLite persistence layer and Flask REST API with proper error handling and validation.
                \item Developed high-performance C++17 matching engine with pybind11 Python bindings achieving 10-50x speedup; thread-safe operations with mutex guards and optimized memory management.
                \item \textbf{SDET Focus:} Authored 50+ pytest unit tests, 18 BDD scenarios (Behave), network/socket tests and load testing suite; created formal TEST\_PLAN.md documenting test cases, risk matrix and acceptance criteria.
                \item Configured GitHub Actions CI/CD with 4 parallel jobs — linting (Pylint/Flake8), unit tests with coverage, BDD tests and build verification; integrated defect tracking via GitHub Issues with release sign-off workflow.
                \item Implemented complete FIX protocol message lifecycle (Logon, Heartbeat, NewOrderSingle, ExecutionReport, OrderCancelRequest) with proper sequence numbering, checksum validation and session management.
                \item Designed real-time WebSocket broadcast system for order book updates, trade notifications and market data dissemination — enabling live dashboard with sub-second latency.
            \end{highlights}
        \end{onecolentry}

        \vspace{0.12 cm}

        \begin{twocolentry}{\textit{\href{https://github.com/Demiserular/MENTY}{GitHub}}}
            \textbf{Menty: Privacy-First Mental Health Companion App}
        \end{twocolentry}
        \vspace{0.06cm}
        \begin{onecolentry}
            \begin{highlights}
                \item Built cross-platform mobile app (iOS/Android) with 6 core modules — mood tracking, CBT journaling, breathing techniques, crisis toolkit, biometric auth and AES-256 encrypted local storage; zero cloud dependency ensuring HIPAA-grade privacy.
                \item Architected modular service layer with React Native (Expo SDK 54) and TypeScript — 15+ reusable components, typed domain models and centralized theme system enabling rapid feature iteration.
                \item Implemented 3-layer security: react-native-biometrics for Face ID/Touch ID, Expo SecureStore for keychain-based key management, and SQLite with field-level encryption plus cryptographic secure deletion.
                \item Configured EAS Build CI/CD pipeline with ESLint/Prettier/Husky pre-commit hooks; achieved WCAG 2.1 accessibility compliance with VoiceOver/TalkBack support and 60fps animations via react-native-reanimated.
                \item Designed offline-first architecture with async storage sync, graceful error handling and comprehensive logging for debugging — zero network dependencies ensuring 100\% uptime reliability.
                \item Published open-source with MIT license, comprehensive README documentation, contribution guidelines and semantic versioning for community collaboration.
            \end{highlights}
        \end{onecolentry}

    \section{Technical Skills}
        \begin{onecolentry}
            \textbf{Languages:} Python, C++, TypeScript, JavaScript, Golang, SQL
        \end{onecolentry}
        \vspace{0.08 cm}
        \begin{onecolentry}
            \textbf{Testing \& QA:} Pytest, Behave (BDD), Jest, Cypress, Postman, Test Planning, Coverage Analysis, Load Testing
        \end{onecolentry}
        \vspace{0.08 cm}
        \begin{onecolentry}
            \textbf{Backend \& Databases:} Flask, FastAPI, Node.js, REST APIs, Socket Programming, SQLite, MySQL, MongoDB
        \end{onecolentry}
        \vspace{0.08 cm}
        \begin{onecolentry}
            \textbf{DevOps \& Tools:} Linux, Git, GitHub Actions, Docker, AWS (EC2/S3), CI/CD Pipelines, Nginx, Shell Scripting
        \end{onecolentry}
        \vspace{0.08 cm}
        \begin{onecolentry}
            \textbf{Frontend:} React, React Native, Next.js, HTML/CSS, WebSocket Integration
        \end{onecolentry}
        \vspace{0.08 cm}
        \begin{onecolentry}
            \textbf{Domain:} FIX Protocol, Financial Systems, Security (AES, JWT, OWASP), Network Protocols
        \end{onecolentry}

    \section{Education}
        \begin{twocolentry}{\textit{2022 – Present}}
            \textbf{ABES Engineering College} \\
            \textit{B.Tech Information Technology, CGPA: 7}
        \end{twocolentry}
        \vspace{0.08 cm}
        \begin{twocolentry}{\textit{2020 – 2021}}
            \textbf{Bethesda Christian Academy} \\
            \textit{Higher Secondary - 86.4\% (CBSE)}
        \end{twocolentry}

    \section{Certifications \& Achievements}
        \begin{onecolentry}
            \begin{highlights}
                \item \textbf{Cybersecurity Virtual Training:} Mastercard through Forage - Completed threat detection and security protocols training
                \item \textbf{AWS Cloud Certification:} Learned about Basics of AWS and Cloud Computing.
                \item \textbf{Smart India Hackathon:} Shortlisted twice (2023, 2024) for secure web application development
                \item \textbf{Leadership Roles:} Led technical outreach in Unnat Bharat Abhiyan and HUCH community initiatives

            \end{highlights}
        \end{onecolentry}

% ------ subtler/professional ------

% ---------------------------------------------------------

% Commit on 2025-01-01
% Commit on 2025-01-02
% Commit on 2025-01-03
% Commit on 2025-01-04
% Commit on 2025-01-05
% Commit on 2025-01-06
\end{document}






