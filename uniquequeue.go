package main

// UniqueQueue is a generic queue that only allows unique entries.
type UniqueQueue[T comparable] struct {
    queue []T
    seen  map[T]struct{}
}

func NewUniqueQueue[T comparable]() *UniqueQueue[T] {
    return &UniqueQueue[T]{
        queue: make([]T, 0),
        seen:  make(map[T]struct{}),
    }
}

func (uq *UniqueQueue[T]) Enqueue(item T) {
    if _, exists := uq.seen[item]; !exists {
        uq.queue = append(uq.queue, item)
        uq.seen[item] = struct{}{}
    }
}

func (uq *UniqueQueue[T]) Dequeue() (item T, ok bool) {
    if len(uq.queue) == 0 {
        var zero T
        return zero, false
    }
    item = uq.queue[0]
    uq.queue = uq.queue[1:]
    return item, true
}

func (uq *UniqueQueue[T]) IsEmpty() bool {
    return len(uq.queue) == 0
}