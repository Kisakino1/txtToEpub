import random

string = "另一种愿望这回若是打下了晋阳必然不会让赵匡胤跑掉"

my_list = list(string)

new_list = random.sample(my_list, len(my_list))

print(new_list)