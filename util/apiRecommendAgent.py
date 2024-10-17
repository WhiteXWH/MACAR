from . import dataProcess


class BaseClass:
    query: str
    recommend_number: int
    model: str

    def try_get_answer(self, temperature=0):
        max_attempts = 10
        attempts = 0
        while attempts < max_attempts:
            try:
                answer = dataProcess.Tool.get_answer_from_gpt(self.model, self.query, temperature)
                return answer

            except Exception as e:
                print(f"{attempts + 1}th Error happening: {e}")

            finally:
                attempts += 1


class Prompt1(BaseClass):
    def __init__(self, recommend_number, programming_query, model):
        self.model = model
        self.query = \
            f'''
    Please recommend {recommend_number} Java API
    methods to me briefly, only give the
    full path of the API methods and no
    need to provide code snippets and
    introductions. Questiones are as
    follow: {programming_query}
    '''


class Agent1BasePrompt2(BaseClass):

    def __init__(self, recommend_number, programming_query, model):
        self.model = model
        self.recommend_number = recommend_number
        self.query = \
            f'''
    As an experienced Java developer, suppose you are writing a Java program, and now you have the following programming problem: {programming_query}.
    Please recommend {self.recommend_number} Java API methods according to the programming problem, only give the full path of the API methods and no need to provide code snippets and introductions.
    For example, given the problem: "How to validate a file path in java?", the answer should be:
    1. java.nio.file.Path.normalize
    2. java.nio.file.Path.resolve
    3. etc....
    '''


class Agent2StructCoT(BaseClass):
    SCoT: str
    nature_language_instructions: str
    testing_requirement: str

    def __init__(self, programming_query, model):
        # super.__init__()
        self.model = model
        self.nature_language_instructions = \
            '''
    Your task is to complete the following code. 
    You should first write a rough problem-solving process using three programming structures (i.e., sequential, branch, and loop structures) and then output the final code. 
    Here are 3 demonstration examples:
    
    '''

        self.SCoT = \
            '''
    example1:
    /** 
    * Write a Java method to find sum of prime numbers between 1 to n. 
    */ 
    Integer sumOfPrimes(Integer n) { 
        // Let's think step by step 
        // Input: n, an integer 
        // Output: sum, an integer 
        // 1. Initialize a list "prime" with True values. 
        // 2. Initialize a variable "p" with 2. 
        // 3. While p * p is less than or equal to n: 
        // 4.  If prime[p] is True: 
        // 5.    Set all the multiples of p to False. 
        // 6.  Increment the variable "p" by 1. 
        // 7. Compute the sum of the prime numbers. 
        // 8. Return the sum. 
        // Write your code here
        
        Integer sum = 0;
        Boolean[] prime = new Boolean[n + 1];
         for (int p = 2; p * p <= n; p++) {
            if (prime[p]) {
                for (int i = p * p; i <= n; i += p) {
                    prime[i] = false;
                }
            }
        }
        for (int i = 2; i <= n; i++) {
            if (prime[i]) {
                sum += i;
            }
        }
        return sum;
    }
    
    example2:    
    /** 
    * Return True is list elements are monotonically increasing or decreasing.
    */
    Boolean monotonic(Double[] arr) {
        // Let's think step by step 
        // Input: arr, an array of doubles
        // Output: flag, a boolean 
        //1: for each element in arr do 
        //2: if the element is greater than its previous element then 
        //3:    l increases 
        //4: if the element is less than its previous element then 
        //5:    l decreases 
        //6: if both increase and decrease then 
        //7:    return False 
        //8: else 
        //9:    return True
        // Write your code here

        Boolean flag = true;
        Boolean increasing = false;
        Boolean decreasing = false;
        for (int i = 1; i < arr.length; i++) {
            if (arr[i] > arr[i - 1]) {
                increasing = true;
            } else {
                decreasing = true;
            }
        }
        if (decreasing && increasing) {
            flag = false;
        } else {
            flag = true;
        }
        return flag;
    }
    
    example3:    
    /** 
    * Please perform character shift transformation on the input string to generate a new string.
    */
    String encrypt(String inStr, int bias) {
        // Let's think step by step
        // Input: in_str, String 
        // Output: out_str, String 
        //1. Initialize an alphabet and a bias. 
        //2. Initialize out_str as ””. 
        //3. for char in in_str: 
        //4.     char.index += bias. 
        //5.     if char.index > 25: 
        //6.         char.index -= 26. 
        //7.     Append the char into out_str. 
        //8. Return out_str
        // Write your code here

    
        StringBuilder outStr = new StringBuilder()
        for (char c : inStr.toCharArray()) {
            if (Character.isLetter(c)) { 
                char base = Character.isUpperCase(c) ? 'A' : 'a'; 
                int charIndex = (c - base + bias) % 26; 
                if (charIndex < 0) {
                    charIndex += 26; 
                }
                outStr.append((char) (base + charIndex)); 
            } else {
                outStr.append(c); 
            }
        }
        return outStr.toString();
        
    '''

        self.testing_requirement = \
            f'''
       //please solve the problem: {programming_query} 
       //The method name and content are not limited.
       //Let's think step by step.
       //Write your code here
       code:
    '''

        # f'''
        #        Based on the above example, please solve the problem: {programming_query}.
        #        The method name and content are not limited.
        #        In addition, you should use "{API}" this API method in your code.
        #        Let's think step by step.
        # '''

        self.query = self.nature_language_instructions + self.SCoT + self.testing_requirement

    @staticmethod
    def get_java_code(answer):
        if type(answer) == str:
            answer = answer.splitlines()

        record = 0
        result = str()
        for i in range(0, len(answer)):
            item = answer[i]
            if "```java" in item or "```java" in item:
                record = i + 1
                break
            elif "import" in item:
                record = i
                break

        for i in range(record, len(answer)):
            result += answer[i] + "\n"

        return result


class Agent3ExtractApiFromCode(BaseClass):
    def __init__(self, model, programming_query, code):
        self.model = model
        self.query = \
            f'''
        You are an experienced Java developer. Now you have the following programming problem: {programming_query}
        Based on the following code snippet, select the API methods from code snippet that you think can solve the programming problem.
        Please note that only select up to 10 API methods and the API method must be related to the programming problem.
        code snippet: {code}
    
    '''
        code_example = \
            '''   
        Your answer only contains the full path of the API methods and no need to provide code snippets and introductions. 
        Noted that if the API methods are used together, you must separate them into separate APIs.
        Only give the full path of the API methods and no need to provide introductions and other information. 
       
        for example, given the programming problem: "Please perform character shift transformation on the input string to generate a new string." ,
        code snippet: 
            String encrypt(String inStr, int bias) {
                     StringBuilder outStr = new StringBuilder()
                        for (char c : inStr.toCharArray()) 
                            if (Character.isLetter(c)) { 
                                char base = Character.isUpperCase(c) ? 'A' : 'a'; 
                                int charIndex = (c - base + bias) % 26; 
                                if (charIndex < 0) {
                                    charIndex += 26; 
                                }
                                outStr.append((char) (base + charIndex)); 
                            } else {
                                outStr.append(c); 
                            }
                        }
                     return outStr.toString();
                } 
        
        the answer format is as follows:
        1.java.lang.StringBuilder.append  
        2.java.lang.String.toCharArray
        ......
    '''
        self.query += code_example


class Agent4LastJudge(BaseClass):

    def __init__(self, programming_query, recommendation_list1, recommendation_list2, model):
        self.model = model
        self.query = \
            f'''
    As an experienced Java developer, suppose you are writing a Java program, and now you have the following programming problem: {programming_query}.
    You must select 10 API methods from the following two API method lists (API list 1 and API list 2) that you think can solve the programming problem.   

    API list1: {recommendation_list1}

    API list2: {recommendation_list2} 

    The 10 selected API methods must be in a single list.    
    Only give the full path of the API methods and no other clarification or information is required, 
    such as code snippets and introductions.
    Also, don't select the same APIs over and over again.

    for example, give the programming problem: "How to sort an array and print the result?"

    API list1: 
    1. java.util.stream.IntStream.boxed
    2. java.util.Arrays.toString
    3. java.util.stream.Stream<T>.sorted

    API list2: 
    1. java.util.Arrays.sort
    2. java.util.Collections.sort
    3. java.lang.System.out.println
    4. java.lang.System.out.printf
    5. java.util.stream.IntStream.of

    the answer format is as follows:
    1. java.util.Arrays.sort
    2. java.util.Collections.sort
    3. java.lang.System.out.println
    4. java.util.stream.IntStream.boxed
    5. etc.....
    '''
