readme temporario para explicar o que tenho feito e como funciona a parte do back-end


BACK-END ()

pyprojct.toml:

     - ficheiro serve para enpacotar o modulo mazegen como um modulo instalavel via pip
     - setuptool e uma ferranta padrao para criar pacotes python
     - wheel gera um ficheiro .wheel
        ex:
            python3 -m build    ele vaii gerar: 
            mazegen-1.0.0-py3-none-any.whl


config.txt:

     - e como o utilizador controla como o labirinto vai ser gerado
     - o valor do height e do width sao qnts celulas o labirinto tera
     - o exit tem coordenadas validas pk: <= x < WIDTH e 0 <= y < HEIGHT
     - o maze vai ser gravado no ficheiro maze.txt em formato hexadecimal
     - o labirinto e perfeito pk vai ter um unico caminho 1 de entrada e 1 de saida


mazegen/generator.py:

     - classe que vai gerar o labirinto ela tem que ser reutilizavel, enpacotada em pip
        ex:
            from mazegen impoet MazeGenerator

            mg = MazeGenerator(20, 15)
            mg = generate


     - constantes bitwise:

        - uso esses valores porque o subject pede que um numero hexadecimal por celula e como
          um hexadecimal representa 4 bits ent cada celula precisa caber de 0000 ate 1111 (0 a 15)

        - e como cada parede ocupa 1 bit fazemos potencias de 2 e tem de ser nesta ordem pk o 
          subject diz que o bit: 0=N, 1=E, 2=S, 3=W

            bit 0 → valor 1
            bit 1 → valor 2
            bit 2 → valor 4
            bit 3 → valor 8

        - por isso converto para binario para saber se a parede esta fechada ou nao: 1-on, 0-off
          ex:
            o numero 5

             . sabemos que o bit0 = 1, bit1 = 2, bit2 = 4, bit3 = 8
               calculamos:
                    . 8 cabe em 5: nao ent comtinua a sobrar 5
                    . 4 cabe em 5: sim ent sobra 1
                    . 2 cabe em 1(de cima): nao sobra 1
                    . 1 cabe em 1: sim

              ou seja 5 em binario e 0101 isso quer dizer que:
                paredes de norte e sul estao fechadas e este e oeste estao abertas




      - construtor:

         - cria uma instancia do gerador uso uma seed para controlar como o labirinto e gerado
           se eu mudar o seed de 42 para 43 o labirinto ja sera diferente



      - grid:

         - cria uma grelha com todas as paredes fechadas [x][y]


      - generate:
        - onde vai estar o algoritmo de backtracking


      - apply_42_pattern:

         - funcao que desenha o '42' dentro do labirinto usando celulas fechadas: OBRIGATORIO



FRONT-END()
