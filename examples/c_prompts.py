"""C 코드 생성용 프롬프트 예시 모음"""

# StarCoder2는 코드 완성 모델입니다.
# 아래 프롬프트들을 generate_c_code.py에서 PROMPTS에 추가하여 사용하세요.

ALGORITHM_PROMPTS = {
    "bubble_sort": """\
#include <stdio.h>

// Sort arr[] of size n using bubble sort (ascending)
void bubble_sort(int arr[], int n) {
    for (int i = 0; i < n - 1; i++) {""",

    "quick_sort": """\
#include <stdio.h>

int partition(int arr[], int low, int high) {
    int pivot = arr[high];
    int i = low - 1;""",

    "merge_sort": """\
#include <stdio.h>
#include <stdlib.h>

void merge(int arr[], int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;""",

    "binary_search": """\
// Returns index of target in sorted arr[], -1 if not found
int binary_search(int arr[], int n, int target) {
    int left = 0, right = n - 1;""",

    "factorial": """\
// Iterative factorial
long long factorial(int n) {
    long long result = 1;
    for (int i = 2; i <=""",

    "fibonacci": """\
// Returns nth Fibonacci number using dynamic programming
long long fibonacci(int n) {
    if (n <= 1) return n;
    long long dp[n + 1];
    dp[0] = 0; dp[1] = 1;""",
}

DATA_STRUCTURE_PROMPTS = {
    "linked_list": """\
#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node* next;
} Node;

Node* create_node(int data) {""",

    "stack": """\
#include <stdio.h>
#include <stdlib.h>
#define MAX_SIZE 1000

typedef struct {
    int data[MAX_SIZE];
    int top;
} Stack;

void stack_init(Stack* s) {
    s->top = -1;
}

void push(Stack* s, int val) {""",

    "queue": """\
#include <stdio.h>
#include <stdlib.h>
#define MAX_SIZE 1000

typedef struct {
    int data[MAX_SIZE];
    int front, rear, size;
} Queue;

void queue_init(Queue* q) {
    q->front = 0; q->rear = -1; q->size = 0;
}

void enqueue(Queue* q, int val) {""",

    "hash_table": """\
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define TABLE_SIZE 101

typedef struct Entry {
    char key[64];
    int value;
    struct Entry* next;
} Entry;

typedef struct {
    Entry* buckets[TABLE_SIZE];
} HashTable;

int hash(const char* key) {""",
}

STRING_PROMPTS = {
    "reverse_string": """\
#include <string.h>

// Reverse string in-place
void reverse_string(char str[]) {
    int left = 0, right = strlen(str) - 1;""",

    "is_palindrome": """\
#include <string.h>
#include <ctype.h>

// Check if string is palindrome (case insensitive)
int is_palindrome(const char* str) {
    int left = 0, right = strlen(str) - 1;""",

    "count_words": """\
#include <string.h>
#include <ctype.h>

// Count words in a string
int count_words(const char* str) {
    int count = 0;
    int in_word = 0;""",
}

FILE_IO_PROMPTS = {
    "read_lines": """\
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Read all lines from file, returns array of strings
char** read_lines(const char* filename, int* count) {
    FILE* fp = fopen(filename, "r");
    if (!fp) return NULL;""",

    "write_csv": """\
#include <stdio.h>

typedef struct {
    int id;
    char name[64];
    float score;
} Record;

// Write records to CSV file
int write_csv(const char* filename, Record* records, int count) {
    FILE* fp = fopen(filename, "w");
    if (!fp) return -1;""",
}

MEMORY_PROMPTS = {
    "dynamic_array": """\
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int* data;
    int size;
    int capacity;
} DynArray;

void dynarray_init(DynArray* arr) {
    arr->data = NULL;
    arr->size = 0;
    arr->capacity = 0;
}

void dynarray_push(DynArray* arr, int val) {""",

    "memory_pool": """\
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char* buffer;
    size_t total;
    size_t used;
} MemPool;

MemPool* pool_create(size_t size) {""",
}

# 전체 프롬프트 목록
ALL_PROMPTS = {
    **ALGORITHM_PROMPTS,
    **DATA_STRUCTURE_PROMPTS,
    **STRING_PROMPTS,
    **FILE_IO_PROMPTS,
    **MEMORY_PROMPTS,
}

if __name__ == "__main__":
    print(f"사용 가능한 프롬프트: {len(ALL_PROMPTS)}개")
    for name in ALL_PROMPTS:
        print(f"  - {name}")
