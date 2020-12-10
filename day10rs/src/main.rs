use std::collections::HashMap;

use ndarray;

fn part2(mut adaptors: Vec<usize>) -> usize {
    adaptors.push(0);
    let max = adaptors.iter().cloned().max().unwrap();
    adaptors.push(max + 3);

    adaptors.sort();

    let reverse_indexes = adaptors
        .iter()
        .cloned()
        .enumerate()
        .map(|(i, e)| (e, i))
        .collect::<HashMap<_, _>>();

    let mut matrix = ndarray::Array2::zeros((adaptors.len(), adaptors.len()));

    for (i, e) in adaptors.iter().enumerate() {
        for r in 1usize..4 {
            if let Some(j) = reverse_indexes.get(&(e + r)) {
                matrix[[i, *j]] = 1;
            }
        }
    }

    let mut m = matrix.clone();
    let n = adaptors.len();
    let mut total = 0;

    for _ in 0..n {
        total += m[[0, n - 1]];
        m = m.dot(&matrix);
    }

    return total;
}

fn main() {
    let inp = vec![
        95, 43, 114, 118, 2, 124, 120, 127, 140, 21, 66, 103, 102, 132, 136, 93, 59, 131, 32, 9,
        20, 141, 94, 109, 143, 142, 65, 73, 27, 83, 133, 104, 60, 110, 89, 29, 78, 49, 76, 16, 34,
        17, 105, 98, 15, 106, 4, 57, 1, 67, 71, 14, 92, 39, 68, 125, 113, 115, 26, 33, 61, 45, 46,
        11, 99, 7, 25, 130, 42, 3, 10, 54, 44, 139, 50, 8, 58, 86, 64, 77, 35, 79, 72, 36, 80, 126,
        28, 123, 119, 51, 22,
    ];

    println!("p2: {}", part2(inp));
}
