# 커스텀한 sharding table 함수
table_name_list = ['abcd', 'efgh', 'ijkl', 'mnop', 'qrst', 'uvwxyz', 'numetc']

def get_sharding_tb_name(user_email: str):
  """
  주어진 이메일 주소를 기반으로 해시 테이블을 할당하는 함수

  Args:
    user_email: 할당할 이메일 주소

  Returns:
    해당 이메일 주소에 할당되는 테이블 이름
  """

  # 이메일 첫 글자를 소문자로 변환하여 비교
  first_letter = user_email[0].lower()

  # 딕셔너리를 활용하여 효율적으로 테이블 할당
  table_mapping = {
      'a': table_name_list[0], 'b': table_name_list[0], 'c': table_name_list[0], 'd': table_name_list[0],
      'e': table_name_list[1], 'f': table_name_list[1], 'g': table_name_list[1], 'h': table_name_list[1],
      'i': table_name_list[2], 'j': table_name_list[2], 'k': table_name_list[2], 'l': table_name_list[2],
      'm': table_name_list[3], 'n': table_name_list[3], 'o': table_name_list[3], 'p': table_name_list[3],
      'q': table_name_list[4], 'r': table_name_list[4], 's': table_name_list[4], 't': table_name_list[4],
      'u': table_name_list[5], 'v': table_name_list[5], 'w': table_name_list[5], 'x': table_name_list[5], 'y': table_name_list[5], 'z': table_name_list[5],
  }

  # 해당하는 테이블이 없을 경우 default 테이블 할당
  return table_mapping.get(first_letter, table_name_list[-1])


if __name__ == "__main__":
    # 예시 사용법
    email1 = "Alice@example.com"
    email2 = "zOrRo@example.com"
    email3 = "123@example.com"

    print("--- hashing and get tablename by email ---")
    print(f"f({email1}) = {get_sharding_tb_name(email1)}")  # 출력: abcd
    print(f"f({email2}) = {get_sharding_tb_name(email2)}")  # 출력: uvwxyz
    print(f"f({email3}) = {get_sharding_tb_name(email3)}")  # 출력: numetc