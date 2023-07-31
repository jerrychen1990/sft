from snippets import jload_lines, get_batched_data
from process_data import *
from tqdm import tqdm
import concurrent.futures





from tqdm import tqdm
from process_data import *

rs = []
func = parse_belle_multiturn_chat

num_threads = 8
batch_size = 10000


def process_batch(batch):
    for item in tqdm(batch[:]):
        tmp = func(item, do_multi_chat=False)
        if not isinstance(tmp, list):
            
            tmp = [tmp]
        tmp =[e for e in tmp if is_valid(e)]
        rs.extend(tmp)
    

raw = jload_lines("/data/glusterfs/chenhao/data/belle_multichat.jsonl", return_generator=True)


with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    # Submit each line to the thread pool for processing
    futures = [executor.submit(process_batch, batch) for batch in get_batched_data(raw, batch_size=5000)]
    concurrent.futures.wait(futures)


print(f"{len(rs)=}")
print(rs[0])

jdump_lines(rs, "./data/belle_multichat.jsonl")




