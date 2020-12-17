use arrayfire::{self, convolve3, dim4};

fn main() {
    let inp: String = r#"""
#...#.#.
..#.#.##
..#..#..
.....###
...#.#.#
#.#.##..
#####...
.#.#.##.
"""#
    .split_whitespace()
    .collect();

    let initial: Vec<_> = inp
        .chars()
        .filter(|&c| c == '#' || c == '.')
        .map(|c| if c == '#' { 1u8 } else { 0u8 })
        .collect();

    let mut a = arrayfire::Array::new(&initial, arrayfire::dim4!(8, 8, 1));

    // setup filter
    let mut filt_n = vec![1u8; 3 * 3 * 3];
    filt_n[3 * 3 + 3 + 1] = 100;
    let filt = arrayfire::Array::new(&filt_n, dim4!(3, 3, 3));

    for i in 0..6 {
        let r = convolve3(
            &a,
            &filt,
            arrayfire::ConvMode::EXPAND,
            arrayfire::ConvDomain::AUTO,
        );

        let is_3 = arrayfire::eq(&r, &3, false);
        let is_102 = arrayfire::eq(&r, &102, false);
        let is_103 = arrayfire::eq(&r, &103, false);

        let is_alive: arrayfire::Array<u8> =
            arrayfire::or(&arrayfire::or(&is_3, &is_102, false), &is_103, false) * 1u8;
        a = is_alive;
    }

    let (n, _) = arrayfire::sum_all(&a);

    println!("alive: {}", n);
}
