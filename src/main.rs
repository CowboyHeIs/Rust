use std::{
    fs,
    io::{prelude::*, BufReader},
    net::{TcpListener, TcpStream},
    thread,
    time::Duration,
};


fn handle_connection(mut stream: TcpStream) {
    let buf_reader = BufReader::new(&mut stream);
    let http_request: Vec<_> = buf_reader
        .lines()
        .map(|result| result.unwrap())
        .take_while(|line| !line.is_empty())
        .collect();

    let request_line = &http_request[0];
    let mut response_output = String::new();

    if request_line.starts_with("GET /bad") {
        let status_line = "HTTP/1.1 404 NOT FOUND";
        let contents = fs::read_to_string("html/error.html").unwrap();
        let length = contents.len();
        response_output.push_str(&format!(
            "{status_line}\r\nContent-Length: {length}\r\n\r\n{contents}"
        ));
    } else {
        let status_line = "HTTP/1.1 200 OK";
        let contents = fs::read_to_string("html/hello.html").unwrap();
        let length = contents.len();
        response_output.push_str(&format!(
            "{status_line}\r\nContent-Length: {length}\r\n\r\n{contents}"
        ));
    }
    let (status_line, filename) = match &request_line[..] {
        "GET / HTTP/1.1" => ("HTTP/1.1 200 OK", "hello.html"),
        "GET /sleep HTTP/1.1" => {
            thread::sleep(Duration::from_secs(10));
            ("HTTP/1.1 200 OK", "hello.html")
        }
        _ => ("HTTP/1.1 404 NOT FOUND", "404.html"),
    };


    stream.write_all(response_output.as_bytes()).unwrap();
}

fn main() {
    let listener = TcpListener::bind("127.0.0.1:7878").unwrap();

    for stream in listener.incoming() {
        let stream = stream.unwrap();
        println!("Connection established!");

        thread::spawn(|| {
            handle_connection(stream);
        });
    }
}