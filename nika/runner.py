from agents import Planner, Query_Reciever, Query_Builder, Query_Executer
from llm import OpenAI_LLM
# from agents.prompts import planner, query_receiver

l = Planner()
# result = l.run(model_name='gpt-3.5-turbo',sys_prompt=planner, usr_prompt='how to project my sales')
# print(result)

# query = Query_Reciever()
# result = query.inference(usr_prompt='what is the total sales of the company in 2020?')
# print(result)


db_schema = f"""
Users (user_id INT, name VARCHAR(255), email VARCHAR(255), city VARCHAR(255), country VARCHAR(255)),
Posts (post_id INT, user_id INT, title VARCHAR(255), content TEXT, created_at DATE),
Comments (comment_id INT, post_id INT, user_id INT, comment_text TEXT, created_at DATE),
Likes (like_id INT, post_id INT, user_id INT, created_at DATE)"
"""


usr_q =  "Find the names of users who have commented on posts created in the last week, but have not liked any posts themselves."
# usr_q = 'how to project my sales'
# result = l.inference(usr_prompt=usr_q, database_schema=db_schema)
# print(result)

plan = {'steps': [{'description': 'Join the Users, Posts, Comments, and Likes tables on the relevant foreign key relationships', 'agent': 'query_builder', 'type': 'join', 'params': {'tables': ['Users', 'Posts', 'Comments', 'Likes'], 'on': [['Users.user_id', 'Comments.user_id'], ['Users.user_id', 'Likes.user_id'], ['Posts.post_id', 'Comments.post_id'], ['Posts.post_id', 'Likes.post_id']]}}, {'description': 'Filter the joined result to include only posts created in the last week', 'agent': 'query_builder', 'type': 'filter', 'params': {'condition': 'Posts.created_at >= DATE_SUB(CURDATE(), INTERVAL 1 WEEK)'}}, {'description': 'Filter the result to exclude users who have liked any posts', 'agent': 'query_builder', 'type': 'filter', 'params': {'condition': 'Likes.user_id IS NULL'}}, {'description': 'Select the names of users from the Users table in the filtered result', 'agent': 'query_builder', 'type': 'select', 'params': {'columns': ['Users.name']}}]}




class Nika:
    def __init__(self):
        self.query = Query_Reciever()
        self.planner = Planner()
        self.query_builder = Query_Builder()
        self.query_executer = Query_Executer()
    
    def run(self,usr_prompt, db_schema):
        user_query = self.query.inference(usr_prompt, db_schema)
        user_query_response = self.query.parse_response(user_query)
        # print(user_query_response)
        if user_query_response['question_type'] == 'non-relevant':
            return user_query_response['additional_info']
        else:
            plan = self.planner.inference(usr_prompt, db_schema)
            planner_response = self.planner.parse_response(plan)
            print(planner_response)
            query_builder_steps = [step for step in planner_response['steps'] if step['agent'] == 'query_builder']
            print(query_builder_steps)
            # print(type(query_builder_steps))
            builder_response = self.query_builder.inference(instructions=query_builder_steps, database_schema=db_schema)
            print(builder_response)
            # print(type(builder_response))
            parsed_builder_response = self.query_builder.parse_response(builder_response)
            # print(type(parsed_builder_response))
            psql_query = parsed_builder_response['SQL_query']
            print(psql_query)
            # for query in psql_query:
            #     result = self.query_executer.execute_query(query)
            #     print(result)
            # return result
            #ececute each query and return the corresponding result
            # for query in psql_query:
            #     result = self.query_executer.execute_query(query)
            #     result
            query_e = psql_query[-1]
            result = self.query_executer.execute_query(query_e)
            return result


 

            
        
        

# for steps in result['steps']:
#     print(steps)
#     print("------------")

# e = Query_Executer()
# result = e.execute_query(query='select * from superstore.orders LIMIT 1')
# print(result)

#SUPERSTORE DB SCHEMA 
DB_S = """
db_name.orders (order_id VARCHAR(255), order_date DATE, ship_date DATE, ship_mode VARCHAR(255), customer_id VARCHAR(255), customer_name VARCHAR(255), segment VARCHAR(255), country VARCHAR(255), city VARCHAR(255), postal_code INT, region VARCHAR(255), product_id VARCHAR(255), category VARCHAR(255), sub_category VARCHAR(255), product_name VARCHAR(255), sales DOUBLE PRECISION, quantity INT, discount DOUBLE PRECISION, profit DOUBLE PRECISION),
db_name.returns (returned VARCHAR(255), order_id VARCHAR(255)),
"""

DB_S_Q = """what is the total sales amount for 2016"""

c = Nika()

result = c.run(usr_prompt=DB_S_Q, db_schema=DB_S)   
print(result)     #

ins = [{'description': 'Filter the orders table to include only orders placed in the year 2017', 'agent': 'query_builder', 'type': 'filter', 'params': {'condition': 'EXTRACT(YEAR FROM order_date) = 2017'}}, {'description': 'Select the sales column from the filtered orders table', 'agent': 'query_builder', 'type': 'select', 'params': {'columns': ['sales']}}]

# b = Query_Builder()
# result = b.inference(instructions=ins, database_schema=DB_S)
# print(result)