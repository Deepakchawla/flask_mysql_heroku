# # # import random
# # # no = random.randint(1000000000000000,9999999999999999)
# # # print(no)
# #
# # import random
# # def uniqueid():
# #     seed = random.getrandbits(32)
# #     while True:
# #        yield seed
# #        seed += 1
# # import itertools
# # unique_sequence = uniqueid()
# # id1 = next(unique_sequence)
# # id2 = next(unique_sequence)
# # id3 = next(unique_sequence)
# # ids = list(itertools.islice(unique_sequence, 1000000000000000))
# # print(id1)
# import hashlib
# import random
# import numpy as np
#
#
# def hash_int(int_num):
#     hashed_num = hashlib.md5(str(int_num).encode())
#     return hashed_num.hexdigest()
#
#
# class RandomIdsGenerator:
#     """
#     Generate random ids from specific numbers of auto generated unique ids.
#     For instance: you maybe want to generate 1000 random user ids from 10 unique ids.
#     How it works: it generate random number in specific range and hash this number using md5
#      and convert it to hexdigest
#     """
#     __slots__ = ['__n_unique_id', '__start_num', '__end_num']
#     MAX_RANGE = 1000000
#
#     def __init__(self, n_unique_id, start_seed = None):
#         """
#         Initialize RandomIdsGenerator
#         :param n_unique_id: number of unique ids you desire
#         :param start_seed: start number of the unique ids,
#                 Default is None that will pick up a number between (0:1000000)
#                 you can can use if you want generate ids in specific ranges.
#         """
#         self.__n_unique_id = n_unique_id
#         self.__start_num = start_seed
#         if not self.__start_num:
#             self.__start_num = random.randrange(RandomIdsGenerator.MAX_RANGE)
#         self.__end_num = self.__start_num + n_unique_id - 1
#
#     def random(self):
#         """
#         Generate single random id
#         :return: random id
#         """
#         random_num = random.randrange(self.__start_num, self.__end_num)
#         return hash_int(random_num)
#
#     def randoms(self, n_ids):
#         """
#         Generate list of random ids
#         :param n_ids: number of id you need to generate
#         :return: list of random ids it might contains duplications
#         """
#         random_numbers = np.random.randint(low=self.__start_num, high=self.__end_num, size=n_ids)
#         v_hash_func = np.vectorize(hash_int)
#         return v_hash_func(random_numbers)
#
#     def get_unique_ids(self):
#         """
#         :return: list of unique ids it randomize from
#         """
#         unique_ids = []
#         print(self.__start_num, self.__end_num)
#         for i in range(self.__start_num, self.__end_num + 1):
#             hashed_num = hashlib.md5(str(i).encode())
#             unique_ids.append(hashed_num.hexdigest())
#         return unique_ids[0]
# random_ids_generator = RandomIdsGenerator(10000)
# print(random_ids_generator.get_unique_ids())
#294980

a = 0
while True:
    import requests
    import random, string
    x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
    xx = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(160))
    url = 'https://chatbot.incubation.bridgelabz.com/qa_predict?question=' + x + '&email_id=' + xx +'czcdzdss@gmail.com&name=fsdfs&phone=null&user_id=5f53a1df2459e9e02dbf8a41&id=5dc15779c346052fe774a8d1'
    results  = requests.get(url)
    a = a +1
    print(a)