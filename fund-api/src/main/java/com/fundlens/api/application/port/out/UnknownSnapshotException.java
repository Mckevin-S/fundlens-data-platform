package com.fundlens.api.application.port.out;

public class UnknownSnapshotException extends RuntimeException {

    public UnknownSnapshotException(String message) {
        super(message);
    }
}
