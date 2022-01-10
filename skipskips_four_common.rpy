screen skipskip_four_screen(towhere):
    timer 15.0 action [Play("audio", "se/sounds/select2.ogg"), Hide('skipskip_four_screen')]

    textbutton "Skip >>":
        action [Play("audio", "se/sounds/select3.ogg"), Stop("music",fadeout=1.0), Stop("soundloop",fadeout=1.0), Hide('skipskip_four_screen'), Jump(towhere)]
        hovered Play("audio", "se/sounds/select.ogg")
        xanchor 0.0
        yanchor 1.0
        xalign 0.05
        yalign 0.5

        style "menubutton"
