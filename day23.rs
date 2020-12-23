fn part2(inp: Vec<u32>) -> u64 {
    let min = *inp.iter().min().unwrap();
    let max = *inp.iter().max().unwrap();

    let mut map = vec![0; inp.len() + 1000000];

    for (a, b) in inp.iter().zip(inp.iter().skip(1)) {
        map[*a as usize] = *b;
    }

    map[*inp.last().unwrap() as usize] = max + 1;

    for i in (max + 1)..1000000 {
        map[i as usize] = i + 1;
    }

    map[1000000] = inp[0];

    let mut current = inp[0];

    for _ in 0..10000000 {
        let a = map[current as usize];
        let b = map[a as usize];
        let c = map[b as usize];
        let after = map[c as usize];

        let mut target = current - 1;
        while target < min || target == a || target == b || target == c {
            if target < min {
                target = 1000001;
            }
            target -= 1;
        }

        map[c as usize] = map[target as usize];
        map[current as usize] = after;
        map[target as usize] = a;
        current = after;
    }

    let a = map[1];
    let b = map[a as usize];

    return a as u64 * b as u64;
}

fn main() {
    let r = part2(vec![3, 2, 6, 5, 1, 9, 4, 7, 8]);
    println!("r = {}", r);
}
