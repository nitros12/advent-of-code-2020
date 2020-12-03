(define not
  (lambda (x)
    (if x
        0
        1)))

(define land
  (lambda (a b)
    (if a b 0)))

(define foreach
  (lambda (l c)
    (if (not (null? l))
        (let ()
          (c (car l))
          (foreach (cdr l) c)))))

(define digit-char?
  (lambda (c)
    (land (<= 48 c) (<= c 57))))

(define char-as-digit
  (lambda (c)
    (- c 48)))

(define parse-int
  (lambda (chrs)
    (define parse-int-inner
      (lambda (chrs so-far)
        (if (null? chrs)
            null
            (if (digit-char? (car chrs))
                (parse-int-inner (cdr chrs) (+ (* so-far 10) (char-as-digit (car chrs))))
                (cons so-far chrs)))))
    (parse-int-inner chrs 0)))

(define take-until
  (lambda (c chrs)
    (if (null? chrs)
        null
        (if (eq? (car chrs) c)
            (cdr chrs)
            (take-until c (cdr chrs))))))

(define count-chars
  (lambda (c chrs)
    (define count-chars-inner
      (lambda (chrs so-far)
        (if (null? chrs)
            so-far
            (count-chars-inner
             (cdr chrs)
             (+ so-far (eq? c (car chrs)))))))
    (count-chars-inner chrs 0)))

(define validate-line-policy-p1
  (lambda (chrs)
    (define min-bound (parse-int chrs))
    (define max-bound (parse-int (take-until 45 (cdr min-bound))))
    (define to-check (take-until 32 (cdr max-bound)))
    (define password (cdr (cdr to-check)))
    (define chars-in-pw (count-chars (car to-check) password))
    (land (<= (car min-bound) chars-in-pw)
          (<= chars-in-pw (car max-bound)))))

(define idx
  (lambda (lst i)
    (if (null? lst)
        null
        (if (eq? i 0)
            (car lst)
            (idx (cdr lst) (- i 1))))))

(define validate-line-policy-p1
  (lambda (chrs)
    (define min-bound (parse-int chrs))
    (define max-bound (parse-int (take-until 45 (cdr min-bound))))
    (define to-check (take-until 32 (cdr max-bound)))
    (define password (cdr (cdr (cdr to-check))))
    (define chars-in-pw (count-chars (car to-check) password))
    (land (<= (car min-bound) chars-in-pw)
          (<= chars-in-pw (car max-bound)))))

(define validate-line-policy-p2
  (lambda (chrs)
    (define idx-one (parse-int chrs))
    (define idx-two (parse-int (take-until 45 (cdr idx-one))))
    (define to-check (take-until 32 (cdr idx-two)))
    (define password (cdr (cdr (cdr to-check))))
    (eq? 1 (+ (eq? (car to-check) (idx password (- (car idx-one) 1)))
              (eq? (car to-check) (idx password (- (car idx-two) 1)))))))

(define day2-part1
  (lambda (inp)
    (define inner
      (lambda (policies so-far)
        (if (null? policies)
            so-far
            (inner (cdr policies)
                   (+ so-far (validate-line-policy-p1 (string-chars (car policies))))))))
    (inner inp 0)))


(define day2-part2
  (lambda (inp)
    (define inner
      (lambda (policies so-far)
        (if (null? policies)
            so-far
            (inner (cdr policies)
                   (+ so-far (validate-line-policy-p2 (string-chars (car policies))))))))
    (inner inp 0)))

(define input
  '(
"6-8 s: svsssszslpsp"
"3-4 n: gncn"
"4-8 v: vkvmvdmvhttvvrgvvwv"

    ))

(display "p1")
(display (day2-part1 input))
(display "p2")
(display (day2-part2 input))
