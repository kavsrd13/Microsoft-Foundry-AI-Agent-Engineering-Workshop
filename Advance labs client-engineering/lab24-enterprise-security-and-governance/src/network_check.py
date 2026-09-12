"""Inspect DNS from the runtime host; private DNS alone does not prove isolation."""
import argparse
import ipaddress
import socket


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('hosts', nargs='+', help='Resource DNS names, not URLs or tokens')
    args = parser.parse_args()
    for host in args.hosts:
        addresses = sorted({item[4][0] for item in socket.getaddrinfo(host, 443)})
        print(host, [{'ip': value, 'private': ipaddress.ip_address(value).is_private} for value in addresses])
    print('Also inspect public-network settings, private endpoint approval, routing and outside-network rejection.')


if __name__ == '__main__':
    main()
