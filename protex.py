#!/usr/bin/env python3
"""
ProTeX v2.00 - Translates Code Prologues to LaTeX (Python Version)
===================================================================

Original Perl version by A. da Silva, 1995.

Revision History (Original Perl Version):
------------------------------------------
  20Dec1995  da Silva  First experimental version.
  10Nov1996  da Silva  First internal release (v1.01).
  28Jun1997  da Silva  Modified so that !DESCRIPTION can appear after
             !INTERFACE, and !INPUT PARAMETERS etc. changed to italics.
  02Jul1997  Sawyer    Added shut-up mode.
  20Oct1997  Sawyer    Added support for shell scripts.
  11Mar1998  Sawyer    Added: file name, date in header, C, script support.
  05Aug1998  Sawyer    Fixed LPChang-bug-support-for-files-with-underscores.
  10Oct1998  da Silva  Introduced -f option for removing source file info
                       from subsection, etc.  Added help (WS).
  06Dec1999  C. Redder Added LaTeX command "\label{sec:prologues}" just 
                       after the beginning of the prologue section.
  13Dec1999  C. Redder Increased flexibility in command-line interface.
                       The options can appear in any order which will allow
                       the user to implement options for select files.
  01Feb1999  C. Redder Added \usepackage commands to preamble of LaTeX
                       document to include the packages amsmath, epsfig,
                       and hangcaption.
  10May2000  C. Redder Revised LaTeX command "\label{sec:prologues}"
                       to "\label{app:ProLogues}".
  10/10/2002 da Silva  Introduced ARGUMENTS keyword, touch ups.
  15Jan2003  R. Staufer Modified table of contents to print only section headers - no descriptions.
  25Feb2003  R. Staufer Added BOPI/EOPI and -i (internal) switch to provide the option
                       of omitting prologue information from output files.

Revision History (Python Version):
-------------------------------------
  - Converted and reorganized from the original Perl version to Python.
  - Added comprehensive documentation and improved command-line parsing.
  05May2023  J. G. de Mattos  Added Shell script support (Python version).
  01Feb2025  J. G. de Mattos  Added a custon style option

-----------------------------------------------------------------------
Command Line Switches:
-----------------------------------------------------------------------
  -h   : Help mode: list command line options
  -b   : Bare mode, meaning no preamble, etc.
  -i   : Internal mode: omit prologues marked !BOPI
  +/-n : New page for each subsection (wastes paper)
  +/-l : Listing mode, default is prologues only
  +/-s : Shut-up mode, i.e., ignore any code from BOC to EOC
  +/-x : No LaTeX mode, i.e., put !DESCRIPTION: in verbatim mode
  +/-f : No source file info
  -A   : Ada code
  -C   : C++ code
  -F   : F90 code (default)
  -S   : Shell script

The options can appear in any order. The options -h and -b affect the input from all files listed on the command line.
Each of the remaining options affects only the input from the files listed after that option and prior to any overriding option.
The plus sign turns off the option. For example, the command-line:
    protex -bnS File1 -F File2.f +n File3.f
will cause the option -n to affect the input from the files File1 and File2.f, but not from File3.f.
The -S option is implemented for File1 but is overridden by -F for File2.f and File3.f.

-----------------------------------------------------------------------
See Also:
  For a more detailed description of ProTeX functionality, DAO Prologue, and other conventions, consult:
    Sawyer, W., and A. da Silva, 1997: ProTeX: A Sample Fortran 90 Source Code Documentation System.
    DAO Office Note 97-11.
"""

import sys
import os
import argparse
from datetime import datetime


def print_notice():
    """Prints the notice header in the LaTeX document.

    This header informs that the document was automatically generated and that
    any changes may be lost upon regeneration.

    Returns:
        None
    """
    print("%                **** IMPORTANT NOTICE *****")
    print("% This LaTeX file was automatically generated by ProTeX (Python version)")
    print("% Any changes made to this file will likely be lost next time")
    print("% it is regenerated from its source. Send questions to your_email@example.com\n")


def print_preamble(custom_style=None):
    """Prints the LaTeX preamble.

    If a custom_style is provided, it uses that style (document class) and includes the corresponding package.
    
    Args:
        custom_style (str, optional): The custom document class or style name to use.
        
    Returns:
        None
    """
    print("%------------------------ PREAMBLE --------------------------")
    if custom_style:
        print("\\documentclass[11pt]{" + custom_style + "}")
    else:
        print("\\documentclass[11pt]{article}")
    
    print("\\usepackage{amsmath}")
    
    # Se o usuário tiver um arquivo de estilo (por exemplo, myStyle.sty), pode incluí-lo:
    if custom_style:
        print("\\usepackage{" + custom_style + "}")
    
    print("\\textheight     9in")
    print("\\topmargin      0pt")
    print("\\headsep        1cm")
    print("\\headheight     0pt")
    print("\\textwidth      6in")
    print("\\oddsidemargin  0in")
    print("\\evensidemargin 0in")
    print("\\marginparpush  0pt")
    print("\\pagestyle{myheadings}")
    print("\\markboth{}{}")
    print("%-------------------------------------------------------------")
    print("\\setlength{\\parskip}{0pt}")
    print("\\setlength{\\parindent}{0pt}")
    print("\\setlength{\\baselineskip}{11pt}")


def print_macros():
    """Prints shorthand macros for common LaTeX commands.

    These macros simplify writing equations, lists, and other elements in the document.

    Returns:
        None
    """
    print("\n%--------------------- SHORT-HAND MACROS ----------------------")
    print("\\def\\bv{\\begin{verbatim}}")
    print("\\def\\ev{\\end{verbatim}}")
    print("\\def\\be{\\begin{equation}}")
    print("\\def\\ee{\\end{equation}}")
    print("\\def\\bea{\\begin{eqnarray}}")
    print("\\def\\eea{\\end{eqnarray}}")
    print("\\def\\bi{\\begin{itemize}}")
    print("\\def\\ei{\\end{itemize}}")
    print("\\def\\bn{\\begin{enumerate}}")
    print("\\def\\en{\\end{enumerate}}")
    print("\\def\\bd{\\begin{description}}")
    print("\\def\\ed{\\end{description}}")
    print("\\def\\({\\left (}")
    print("\\def\\){\\right )}")
    print("\\def\\[{\\left [}")
    print("\\def\\]{\\right ]}")
    print("\\def\\<{\\left \\langle}")
    print("\\def\\>{\\right \\rangle}")
    print("\\def\\cI{{\\cal I}}")
    print("\\def\\diag{\\mathop{\\rm diag}}")
    print("\\def\\tr{\\mathop{\\rm tr}}")
    print("%-------------------------------------------------------------")


def do_beg(state, bare):
    """Begins the LaTeX document by printing the header and initial commands.

    If bare mode is not active and the header has not been printed yet,
    this function prints the title, author, date, table of contents, and starts a new page.

    Args:
        state (dict): Global state of the document.
        bare (bool): Indicates whether bare mode is active.

    Returns:
        None
    """
    if bare:
        return
    if not state["begdoc"]:
        if state["tpage"]:
            print("\\title{" + state["title"] + "}")
            print("\\author{{\\sc " + state["author"] + "}\\\\ {\\em " + state["affiliation"] + "}}")
            print("\\date{" + state["doc_date"] + "}")
        print("\\begin{document}")
        if state["tpage"]:
            print("\\maketitle")
        print("\\tableofcontents")
        print("\\newpage")
        state["begdoc"] = True


def do_eoc(state):
    """Ends a code block in verbatim mode.

    If a verbatim block is active, this function prints the command
    to end the environment and updates the state.

    Args:
        state (dict): Global state of the document.

    Returns:
        None
    """
    if state["verb"]:
        print("\\end{verbatim}")
        state["verb"] = False
    state["source"] = False


def set_missing(state):
    """Resets required information markers in the prologue.

    Updates the state to indicate that no required information (such as the routine name
    or description) has been captured yet.

    Args:
        state (dict): Global state of the document.

    Returns:
        None
    """
    state["have_name"] = False
    state["have_desc"] = False
    state["have_intf"] = False
    state["have_hist"] = False
    state["name_is"] = "UNKNOWN"


def process_file(f, filename, state, tokens, opts):
    """Processes a source file and generates the corresponding LaTeX output.

    This function reads the file line by line, interprets documentation markers
    (e.g., !BOI, !BOP, !ROUTINE:, !IROUTINE:, !DESCRIPTION:, etc.), and prints the
    corresponding LaTeX commands.

    Args:
        f (file-like object): Open file object for reading.
        filename (str): Name of the file (or '-' for STDIN).
        state (dict): Global state of the document.
        tokens (dict): Dictionary of markup tokens for the selected language.
        opts (argparse.Namespace): Command-line options.

    Returns:
        None
    """
    # Determine base file name and format it (replace underscores with "\_")
    file_basename = os.path.basename(filename) if filename != '-' else "Standard Input"
    file_basename = file_basename.replace("_", "\\_")
    file_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("\n\\markboth{Left}{Source File: %s,  Date: %s}\n" % (file_basename, file_date))
    
    for line in f:
        line = line.rstrip("\n").lstrip()
        fields = line.split(maxsplit=9999)
        # If the line starts with "!", then the real marker is at position 1.
        mi = 0
        if fields and fields[0] == '!':
            mi = 1

        # If there are not enough tokens (e.g., the line is just "!"), skip the line.
        if len(fields) <= mi:
            continue

        # --- Processing markers ---
        # !QUOTE:
        if len(fields) > mi and fields[mi] == '!QUOTE:':
            print(" ".join(fields[mi+1:]))
            continue

        # Introduction start: !BOI
        if fields[mi] == tokens["boi"]:
            state["intro"] = True
            continue

        # Process Introduction data (e.g., !TITLE:, !AUTHORS:, etc.)
        if state["intro"] and len(fields) > mi+1:
            marker = fields[mi+1]
            if marker == '!TITLE:':
                if mi == 1:
                    fields.pop(0)  # Remove the extra "!" token
                fields.pop(0)  # Remove the !TITLE: marker
                state["title"] = " ".join(fields)
                state["tpage"] = True
                continue
            elif marker == '!AUTHORS:':
                if mi == 1:
                    fields.pop(0)
                fields.pop(0)
                state["author"] = " ".join(fields)
                state["tpage"] = True
                continue
            elif marker == '!AFFILIATION:':
                if mi == 1:
                    fields.pop(0)
                fields.pop(0)
                state["affiliation"] = " ".join(fields)
                state["tpage"] = True
                continue
            elif marker == '!DATE:':
                if mi == 1:
                    fields.pop(0)
                fields.pop(0)
                state["doc_date"] = " ".join(fields)
                state["tpage"] = True
                continue
            elif marker == '!INTRODUCTION:':
                do_beg(state, opts.bare)
                print(" %..............................................")
                if mi == 1:
                    fields.pop(0)
                fields.pop(0)
                print("\\section{" + " ".join(fields) + "}")
                continue
        if fields[mi] == tokens["eoi"]:
            print("\n %/////////////////////////////////////////////////////////////")
            print("\\newpage")
            state["intro"] = False
            continue

        # Prologue start: !BOP
        if fields[mi] == tokens["bop"]:
            if state["source"]:
                do_eoc(state)
            print("\n %/////////////////////////////////////////////////////////////")
            do_beg(state, opts.bare)
            if not state["first"]:
                print("\n\\mbox{}\\hrulefill\\")
            else:
                if not opts.bare:
                    print("\\section{Routine/Function Prologues} \\label{app:ProLogues}")
            state["first"] = False
            state["prologue"] = True
            state["verb"] = False
            state["source"] = False
            set_missing(state)
            continue

        # Internal prologue start: !BOPI
        if fields[mi] == tokens["bopi"]:
            if opts.internal:
                state["prologue"] = False
            else:
                if state["source"]:
                    do_eoc(state)
                print("\n %/////////////////////////////////////////////////////////////")
                do_beg(state, opts.bare)
                if not state["first"]:
                    print("\n\\mbox{}\\hrulefill\\")
                else:
                    if not opts.bare:
                        print("\\section{Routine/Function Prologues} \\label{app:ProLogues}")
                state["first"] = False
                state["prologue"] = True
                state["verb"] = False
                state["source"] = False
                set_missing(state)
            continue

        # !MODULE:
        if state["prologue"] and fields[mi] == '!MODULE:':
            if mi == 1:
                fields.pop(0)
            fields.pop(0)
            module_name = " ".join(fields).replace("_", "\\_")
            if opts.n:
                print("\\newpage")
            if not opts.f:
                print("\\subsection{Fortran:  Module Interface %s (Source File: %s)}\n" % (module_name, file_basename))
            else:
                print("\\subsection{Fortran:  Module Interface %s}\n" % module_name)
            state["have_name"] = True
            state["have_intf"] = True
            state["not_first"] = True
            continue

        # !ROUTINE:
        if state["prologue"] and fields[mi] == '!ROUTINE:':
            if mi == 1:
                fields.pop(0)
            fields.pop(0)
            routine_name = " ".join(fields).replace("_", "\\_")
            if opts.n and state["not_first"]:
                print("\\newpage")
            if not opts.f:
                print("\\subsubsection{%s (Source File: %s)}\n" % (routine_name, file_basename))
            else:
                print("\\subsubsection{%s}\n" % routine_name)
            state["have_name"] = True
            state["not_first"] = True
            continue

        # !IROUTINE:
        if state["prologue"] and fields[mi] == '!IROUTINE:':
            if mi == 1:
                fields.pop(0)
            fields.pop(0)
            routine_name = " ".join(fields).replace("_", "\\_")
            words = routine_name.split()
            label = words[1] if len(words) > 1 else ""
            print("\\subsubsection [%s]{%s}\n" % (label, routine_name))
            state["have_name"] = True
            continue

        # !DESCRIPTION:
        if state["prologue"] and "!DESCRIPTION:" in line:
            if state["verb"]:
                print("\\end{verbatim}")
                print("{\\sf DESCRIPTION:\\\\ }")
                print("")
                state["verb"] = False
            if opts.nolatex:
                print("\\begin{verbatim}")
                state["verb"] = True
            else:
                parts = line.split()
                start = 1 if parts[0] == '!' else 0
                print(" ".join(parts[start+1:]))
            state["have_desc"] = True
            continue

        # Process optional keyword markers (e.g., !INTERFACE:, !REVISION HISTORY:, etc.)
        processed_key = False
        if state["prologue"]:
            for key in opts.keys:
                if key in line:
                    if state["verb"]:
                        print("\\end{verbatim}")
                        state["verb"] = False
                    else:
                        print("\n\\bigskip")
                    label = key[1:]  # Remove the "!" from the marker
                    if any(x in line for x in ["USES", "INPUT", "OUTPUT", "PARAMETERS", "VALUE", "ARGUMENTS"]):
                        print("{\\em " + label + "}")
                    else:
                        print("{\\sf " + label + "}")
                    print("\\begin{verbatim}")
                    state["verb"] = True
                    processed_key = True
                    break
            if processed_key:
                continue

        # End of prologue: !EOP or !EOPI
        if fields[mi] in (tokens["eop"], tokens["eopi"]):
            if state["verb"]:
                print("\\end{verbatim}")
                state["verb"] = False
            state["prologue"] = False
            continue

        # Code section: !BOC and !EOC
        if fields[mi] == tokens["boc"]:
            print("\n %/////////////////////////////////////////////////////////////")
            state["first"] = False
            state["prologue"] = False
            state["source"] = True
            print("\n\\begin{verbatim}")
            state["verb"] = True
            continue
        if fields[mi] == tokens["eoc"]:
            do_eoc(state)
            state["prologue"] = False
            continue

        # Example prologue: !BOE and !EOE
        if fields[mi] == tokens["boe"]:
            if state["source"]:
                do_eoc(state)
            print("\n %/////////////////////////////////////////////////////////////")
            state["first"] = False
            state["prologue"] = True
            state["verb"] = False
            state["source"] = False
            continue
        if fields[mi] == tokens["eoe"]:
            if state["verb"]:
                print("\\end{verbatim}")
                state["verb"] = False
            state["prologue"] = False
            continue

        # If in prologue or introduction, print the line (removing the initial comment token if present)
        if state["prologue"] or state["intro"]:
            if line.startswith(tokens["comment"]):
                line = line[len(tokens["comment"]):]
            print(line)
            continue

        # If in code source section, print the line as-is.
        if state["source"]:
            print(line)
            continue

    # End of file processing
    print("")
    if state["source"]:
        do_eoc(state)
    print("%...............................................................")


def main():
    """Main function that parses command-line arguments and generates the documentation.

    Reads command-line arguments, configures the markup tokens based on the selected language
    (Fortran90, Ada, C++, or Shell), initializes the global document state, and processes each
    provided file to generate LaTeX output.

    Returns:
        None
    """
    parser = argparse.ArgumentParser(
        description="ProTeX - Processes documentation for LaTeX (Python version)"
    )
    parser.add_argument("files", nargs="*", help="Source files (use '-' for STDIN)")
    parser.add_argument("-b", "--bare", action="store_true", help="Bare mode: no preamble")
    parser.add_argument("-A", action="store_true", help="Ada code")
    parser.add_argument("-C", action="store_true", help="C++ code")
    parser.add_argument("-F", action="store_true", help="Fortran90 code (default)")
    parser.add_argument("-S", action="store_true", help="Shell script")
    parser.add_argument("--n", action="store_true", help="New page for each subsection")
    parser.add_argument("--l", action="store_true", help="Listing mode (only prologues)")
    parser.add_argument("--s", action="store_true", help="Shut-up mode (ignore code between BOC and EOC)")
    parser.add_argument("--x", dest="nolatex", action="store_true", help="No LaTeX mode (print !DESCRIPTION in verbatim)")
    parser.add_argument("--f", action="store_true", help="Do not display source file info")
    parser.add_argument("--i", dest="internal", action="store_true", help="Internal mode: omit prologues !BOPI/EOPI")
    parser.add_argument("--keys", nargs="*", default=[
        "!INTERFACE:", "!USES:", "!PUBLIC TYPES:", "!PRIVATE TYPES:",
        "!PUBLIC MEMBER FUNCTIONS:", "!PRIVATE MEMBER FUNCTIONS:",
        "!PUBLIC DATA MEMBERS:", "!PARAMETERS:", "!ARGUMENTS:",
        "!DEFINED PARAMETERS:", "!INPUT PARAMETERS:", "!INPUT/OUTPUT PARAMETERS:",
        "!OUTPUT PARAMETERS:", "!RETURN VALUE:", "!REVISION HISTORY:",
        "!BUGS:", "!SEE ALSO:", "!SYSTEM ROUTINES:", "!FILES USED:",
        "!REMARKS:", "!TO DO:", "!CALLING SEQUENCE:", "!AUTHOR:",
        "!CALLED FROM:", "!LOCAL VARIABLES:"
    ], help="List of optional keyword markers")
    parser.add_argument("--style", type=str, default=None,
                        help="Custom LaTeX style or document class to use (e.g., 'myStyle')")
    opts = parser.parse_args()

    # Determine the language; Fortran90 is the default.
    lang = 'F'
    if opts.A:
        lang = 'A'
    elif opts.C:
        lang = 'C'
    elif opts.S:
        lang = 'S'
    
    language_tokens = {
        'F': {
            "comment": "!",
            "bop": "!BOP",
            "eop": "!EOP",
            "boi": "!BOI",
            "eoi": "!EOI",
            "bopi": "!BOPI",
            "eopi": "!EOPI",
            "boc": "!BOC",
            "eoc": "!EOC",
            "boe": "!BOE",
            "eoe": "!EOE",
        },
        'A': {
            "comment": "--",
            "bop": "--BOP",
            "eop": "--EOP",
            "boi": "--BOI",
            "eoi": "--EOI",
            "bopi": "--BOPI",
            "eopi": "--EOPI",
            "boc": "--BOC",
            "eoc": "--EOC",
            "boe": "--BOE",
            "eoe": "--EOE",
        },
        'C': {
            "comment": "//",
            "bop": "//BOP",
            "eop": "//EOP",
            "boi": "//BOI",
            "eoi": "//EOI",
            "bopi": "//BOPI",
            "eopi": "//EOPI",
            "boc": "//BOC",
            "eoc": "//EOC",
            "boe": "//BOE",
            "eoe": "//EOE",
        },
        'S': {
            "comment": "#",
            "bop": "#BOP",
            "eop": "#EOP",
            "boi": "#BOI",
            "eoi": "#EOI",
            "bopi": "#BOPI",
            "eopi": "#EOPI",
            "boc": "#BOC",
            "eoc": "#EOC",
            "boe": "#BOE",
            "eoe": "#EOE",
        }
    }
    tokens = language_tokens[lang]

    global comment_string
    comment_string = tokens["comment"]

    # Global state of the document
    state = {
        "intro": False,
        "prologue": False,
        "first": True,
        "source": False,
        "verb": False,
        "tpage": False,
        "begdoc": False,
        "not_first": False,
        "have_name": False,
        "have_desc": False,
        "have_intf": False,
        "have_hist": False,
        "name_is": "UNKNOWN",
        "title": "",
        "author": "",
        "affiliation": "",
        "doc_date": ""
    }

    files = opts.files if opts.files else ['-']
    
    print_notice()
    if not opts.bare:
        print_preamble(opts.style)
    print_macros()

    for filename in files:
        if filename == '-' or filename == '':
            process_file(sys.stdin, filename, state, tokens, opts)
        else:
            with open(filename, 'r') as f:
                process_file(f, filename, state, tokens, opts)
    
    if not opts.bare:
        print("\\end{document}")


if __name__ == "__main__":
    main()
