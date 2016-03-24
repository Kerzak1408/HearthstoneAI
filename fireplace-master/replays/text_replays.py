def log_text_replay(player1, player2):     
    write_line_to_file(f1, "")
    write_line_to_file(f1,"***********************************************************************************************************************")
    write_line_to_file(f1,"HAND 2: " + str(player2.hand))        
    write_line_to_file(f1,"HERO 2: Health = " + str(game.player2.hero.health) + ", Armor = " + str(game.player2.hero.armor) + ", Mana = " + str(game.player2._max_mana))
    field2 = "FIELD 2: "
    for minion in player2.field:
        field2 = field2 + "(" +  str(minion.atk) + ", " + minion.name + ", " + str(minion.health) + "); "
    write_line_to_file(f1,field2)
    write_line_to_file(f1,"-----------------------------------------------------------------------------------------------------------------------")
    field1 = "FIELD 1: "
    for minion in player1.field:
        field1 = field1 + "(" +  str(minion.atk) + ", " + minion.name + ", " + str(minion.health) + "); "
    write_line_to_file(f1,field1)
    write_line_to_file(f1,"HERO 1: Health = " + str(game.player1.hero.health) + ", Armor = " + str(game.player2.hero.armor) + ", Mana = " + str(game.player1._max_mana))
    write_line_to_file(f1,"HAND 1: " + str(player1.hand))
     
    write_line_to_file(f1,"***********************************************************************************************************************")
    write_line_to_file(f1,"")