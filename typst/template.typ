// The project function defines how your document looks.
// It takes your content and some metadata and formats it.
// Go ahead and customize it to your liking!
#let project(title: "", subtitle: "", abstract: [], authors: (), body) = {
  // Set the document's basic properties.
  set document(author: authors.map(a => a.name), title: title)
  set page(numbering: "1", number-align: center, margin: (x: 15mm, y: 25mm))
  set text(font: "New Computer Modern", lang: "en", ligatures: true)
  set cite(style: "numerical")
  show math.equation: set text(weight: 400)

  // Set paragraph spacing.
  show par: set block(above: 0.75em, below: 0.75em)

  set heading(numbering: "1.1")
  set par(leading: 0.58em)

  // Title row.
  align(center)[
    #block(text(weight: 700, 1.75em, title))
    #block(text(weight: 400, 1.35em, subtitle))
  ]

  // Author information.
  pad(
    top: 0.3em,
    bottom: 0.3em,
    x: 2em,
    grid(
      columns: (1fr,) * calc.min(3, authors.len()),
      gutter: 1em,
      ..authors.map(author => align(center)[
        *#author.name* (#author.affiliation)
      ]),
    ),
  )

  // Abstract.
  pad(
    x: 8mm,
    align(center)[
      #heading(
        outlined: false,
        numbering: none,
        text(0.85em, smallcaps[Abstract]),
      )
      #abstract
    ],
  )

  set par(justify: true)
  show: columns.with(2, gutter: 2em)

  body

  bibliography("t3000.bib")
}