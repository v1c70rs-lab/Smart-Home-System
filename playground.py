# FLAVORS = [
#     "Banana",
#     "Chocolate",
#     "Lemon",
#     "Pistachio",
#     "Raspberry",
#     "Strawberry",
#     "Vanilla",
# ]

# gewist = []

# for first_flavor in FLAVORS:
#     for second_flavor in FLAVORS:
#         if first_flavor != second_flavor:
#             if second_flavor in gewist:
#                 continue
#             gewist.append(first_flavor)
#             print(f"{first_flavor}, {second_flavor}")



# def dist(points):
#     largest = max(points)
#     smallest = min(points)
#     answer = largest - smallest
#     return answer

# dist([1, 2, 3])

# dist([1, 2, 3, 2.5])

# dist([1, 2, 3, 2.5, 3.5])

# dist([1, 2, 3, 2.5, 3.5, 120])

# dist([1, 2, 3, 2.5, 3.5, 120, -1000])



# for i in range(1001):
#     if i % 7 == 0:
#         sum = 0
#         for digit in str(i):
#             sum += int(digit)
#         if sum % 3 == 0:
#             sum = 0
#             print(i)
#         else:
#             sum = 0



# import math

# def is_prime(n):
#     if n <= 1:
#         print("Kan niet")
#     else:
#         is_prime = True
#         for i in range(2, int(math.sqrt(n)) + 1):
#             if n % i == 0:
#                 is_prime = False
#                 break
#         print(is_prime)

# is_prime(11)



# list = [(87, "Hylkje"), (85, "Merel",), (76, "Robert"), (102, "Jasper")]

# sortedList = sorted(list, reverse=True)
# print(sortedList)

# sortedList = sorted(list, key=lambda x: (x[1]))
# print(sortedList)



# list = []
# for i in range(100, 151):
#     print("-------------------------")
#     for x in range(2, i):
#         is_prime = True
#         print(f"{i} / {x} = REST {i % x}")
#         if i % x == 0:
#             print("geen priem")
#             is_prime = False
#             break
#     if is_prime == True:
#         list.append(i)

# print(str(list)[1:-1])



# def sum_primes(number):
#     sum_primes = 0
#     for getal in range(2, number):
#         print("-------------------------")
#         is_prime = True
#         for deler in range(2, getal):
#             print(f"{getal} / {deler} = REST {getal % deler}")
#             if getal % deler == 0:
#                 is_prime = False
#                 print("geen priem")
#                 break
#         if is_prime == True:
#             sum_primes += getal
#     return sum_primes

# uitkomst = sum_primes(5)
# print(uitkomst)



# for x in range(100000001,200000000):
#     print(x)
#     is_prime = True
#     for deler in range(2, x):
#         if x % deler == 0:
#             print(f"{x} / {deler} = REST {x % deler}")
#             is_prime = False
#             break
#     if is_prime == True:
#         print(x, is_prime)
#         break



# from datetime import datetime

# x = datetime.now()

# date = x.strftime("%Y-%m-%d")
# time = x.strftime("%H:%M:%S")

# print(f"Today is {date} and it is {time}.")



# referenceCardlist = ['S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'SJ', 'SQ', 'SK', 'SA', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'HJ', 'HQ', 'HK', 'HA', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'DJ', 'DQ', 'DK', 'DA', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'CJ', 'CQ', 'CK', 'CA']

# def missing_card(cards):
#     cardlist = cards.split()
#     for x in referenceCardlist:
#         flag = False
#         for i in cardlist:
#             if x == i:
#                 flag = True
#                 break
#         if flag == False:
#                 return(x)

# missing_card(
#         "S2 S3 S4 S5 S6 S7 S8 S9 S10 SJ SQ SK SA "
#         "H2 H3 H4 H5 H6 H7 H8 H9 H10 HJ HQ HK HA "
#         "D2 D3 D4 D5 D6 D7 D8 D9 D10 DJ DQ DK DA "
#         "C2 C3 C4 C5 C6 C7 C8 C9 C10 CJ CQ "
# )



# from itertools import zip_longest

# def from_roman_numeral(roman_numeral):
#     lijst = []
#     kaas = range(52)
#     for x in roman_numeral:
#         match x:
#             case "I":
#                 x = 1
#                 lijst.append(x)
#             case "V":
#                 x = 5
#                 lijst.append(x)
#             case "X":
#                 x = 10
#                 lijst.append(x)
#             case "L":
#                 x = 50
#                 lijst.append(x)
#             case "C":
#                 x = 100
#                 lijst.append(x)
#             case "D":
#                 x = 500
#                 lijst.append(x)
#             case "M":
#                 x = 1000
#                 lijst.append(x)

#     print(lijst)

#     getalletje = 0
    
#     aftrekken = False

#     for x, i in zip_longest(lijst, lijst[1:], fillvalue=x):
        
#         if aftrekken == True:
#             aftrekken = False
#             continue

#         if x < i:
#             aftrekken = True
#             print(f"aftrekken: {i} - {x} = {i - x}")
#             getalletje += i - x
#         else:
#             print(x)
#             getalletje += x
#     print(getalletje)
#     return getalletje

# from_roman_numeral("XL")



# from datetime import datetime, timedelta

# def friday_the_13th():
#     current_time = datetime.now()
#     weekday = current_time.weekday()
#     first_round = True

#     while(True):
#         # als de eerste ronde gelijk staat aan False tel 1 dag bij current_time op
#         if first_round == False:
#             current_time += timedelta(days=1)
#             weekday = current_time.weekday()
#             print(weekday)

#         if weekday == 4:
#             print("Het is vrijdag")
#             print(current_time.date())
#             format = current_time.date().strftime("%d")

#             if format == "13":
#                 print("Het is vrijdag de 13e")
#                 format = current_time.date().strftime("%Y-%m-%d")
#                 return format

#         first_round = False

# friday_the_13th()



# import unicodedata

# reference_alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
#                       "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

# left = "New York -Times"
# right = "monkeys write"

# def is_anagram(left, right):

#     anagrams = []
#     round_right_word = False
#     left_word = ""
#     right_word = ""
#     left = left.replace(" ", "")
#     right = right.replace(" ", "")

#     for word in left, right:
#         if left and right:
#             for letter in word:
#                 decomposed = unicodedata.decomposition(letter)
#                 decomposed = decomposed.split()
#                 if decomposed:
#                     print(decomposed)
#                     for code in decomposed:
#                         unicode = ''.join('\\u' + code)
#                         unicode_chars = unicode.encode('utf-8').decode('unicode_escape')
#                         composed = unicodedata.normalize('NFC', unicode_chars)

#                         # maak ze voor de check allemaal lowercase
#                         composed_lowercase = composed.lower()

#                         # nu checken wij alle characters of deze wel a t/m z zijn
#                         if composed_lowercase in reference_alphabet:
#                             if round_right_word != True:
#                                 left_word += composed_lowercase
#                             else:
#                                 right_word += composed_lowercase
#                             print(f"{letter} gedecomposeerd tot {composed_lowercase}")
#                 else:
#                     lowercase_letter = letter.lower()
                    
#                     if lowercase_letter in reference_alphabet:   
#                         if round_right_word != True:
#                             left_word += lowercase_letter
#                         else:
#                             right_word += lowercase_letter
#                     else:
#                         print("Letter zit niet in alphabet")
#                     print("Er valt niks te decomposeren")

#             round_right_word = True
#         else:
#             print("Domme dikke lul, je moet wel een waarde meegeven!")
#             return False

#     # check nu of ze gelijke lengte zijn, zo nee, dan weg ermee
#     if len(left_word) == len(right_word):
#         anagrams.append(left_word)
#         anagrams.append(right_word)
#         print("Beide woorden zijn even lang")
#     else:
#         print("Beide woorden zijn niet even lang dus het kunnen nooit anagrammen van elkaar zijn, lul!")
#         return False
    
#     copy_left_word = left_word
#     copy_right_word = right_word

#     # check nu of het anagrammen zijn
#     for letter in copy_left_word:
#         if letter in copy_right_word:
#             copy_left_word = copy_left_word.replace(letter, "", 1)
#             copy_right_word = copy_right_word.replace(letter, "", 1)
#             print(f"{letter} is in right_word")
#         else:
#             print(f"Dit zijn geen anagrammen, want de \"{letter}\" in \"{copy_left_word}\" komt niet voor in \"{copy_right_word}\"")
#             return False
    
#     print(f"\"{copy_left_word}\" en \"{copy_right_word}\" zijn anagrammen van elkaar!")

#     return True

# boolean = is_anagram(left, right)
# print(boolean)



# def fibonacci(n):
#     fibonacci_list = []
#     preprevious_num = 0
#     previous_num = 1
#     for x in range(1, n+1):
#         if x == 1:
#             fibonacci_list.append(1)
#             continue
#         new_num = preprevious_num + previous_num
#         preprevious_num = previous_num
#         previous_num = new_num
#         fibonacci_list.append(new_num)
#     return fibonacci_list

# print(fibonacci(2))



# def how_to_pay(amount, currency):
    
#     centjes = amount
#     smaller_amount = []
#     easy_payment = {}

#     if amount in currency:
#         return {amount: 1}
    
#     while centjes != 0:
        
#         for x in currency:
#             if x <= centjes:
#                 smaller_amount.append(x)

#         highest_currency = max(smaller_amount)
#         centjes -= highest_currency
        
#         if highest_currency in easy_payment:
#             easy_payment[highest_currency] += 1
#         else:
#             easy_payment[highest_currency] = 1
        
#         smaller_amount.clear()
#         print(centjes, easy_payment)
    
#     return easy_payment

# print(how_to_pay(198, [1, 2, 5, 10, 20, 50, 100, 200, 500]))



# alice = ['Ⅱ', 'Ⅳ', 'XIX', 'XV', 'Ⅳ', 'Ⅱ']

# bob = ['Ⅳ', 'Ⅲ', 'Ⅱ', 'XX', 'Ⅱ', 'XX']

# silvester = ['XVⅢ', 'XIX', 'Ⅲ', 'I', 'Ⅲ', 'XVⅢ']

# def love_meet(bob, alice):

#     same_district = set(x for x in bob if x in alice)
    
#     return(same_district)

# print(love_meet(bob, alice))

# def affair_meet(bob, alice, silvester):

#     same_district_wo_bob = set(x for x in alice if x in silvester and x not in bob)

#     return(same_district_wo_bob)

# print(affair_meet(bob, alice, silvester))



# import time

# # in deze opdracht dien je de ingesloten cijfers door te schuiven (met uitsluiting van het begin en eind cijfer)
# deck = [1, 2, 3, 4, 5, 6]

# def perfect_shuffle(deck):
    
#     mid = len(deck) // 2

#     left_halve = deck[:mid]
#     right_halve = deck[mid:]

#     shuffled_deck = []

#     for items in zip(left_halve, right_halve):
#         shuffled_deck.extend(items)

#     print(shuffled_deck)

#     return shuffled_deck

# shuffled_deck = perfect_shuffle(deck)
    
# while(True):

#     shuffled_deck = perfect_shuffle(shuffled_deck)
    
    
#     time.sleep(1)



# import sys

# try:
#     print(sys.argv[1])
# except(IndexError):
#     print("Not enough parameters.")



# my_class = [['Kermit Wade', 27], ['Hattie Schleusner', 67], ['Ben Ball', 5], ['William Lee', 2],['Zen Jack', 26], ['Luigi Austin', 50], ['Ben Benson', 70], ['John Ann', 21]]


# def select_student(students, threshold):
#     dict = {'Accepted': [],
#             'Refused': []}
#     for item in students:
#         if item[1] >= threshold:
#             dict['Accepted'] += [item]
#         else:
#             dict['Refused'] += [item]
#     for key, value in dict.items():
#         if key == 'Accepted':
#             dict[key] = sorted(value, key=lambda index : index[1], reverse=True)
#         else:
#             dict[key] = sorted(value, key=lambda index : index[1])

#     return dict

# students = select_student(my_class, 20)
# print(students)



# import time

# def flatten(obj):
    
#     flat_list = []
    
#     for element in obj:
#         if isinstance(element, list):
#             flat_list.extend(flatten(element))
#         else:
#             flat_list.append(element)
        
#     return flat_list

# x = flatten([[1], 2, [[3, 4], 5], [[[]]], [], [[[6]]], 7, 8, []])

# print(x)



# import math

# def check_adam_number(num):

#     square = str(num**2)
#     reverse_square = int(str(square)[::-1])
    
#     square_root = int(math.sqrt(reverse_square))
#     reverse_square_root = int(str(square_root)[::-1])
        
#     return reverse_square_root == num

# print(check_adam_number(13))



# def mul(numbers):
#     res = 1
#     for i in numbers:
#         res = res * i
#     return res
# print(mul([6,5,4]))



def battery_charge(percentage):
    
    rounded = round(percentage, -1)
    decimaal = int(rounded / 10 + 1)
    decimaaltje = 10 - decimaal + 2

    charge_list = "[          ]"
    charge_list = charge_list[:decimaal].replace(" ","❚") + charge_list[-decimaaltje:]

    print(f"{charge_list}")
    print(f"{percentage}%")

battery_charge(40)
