package org.feup.cmov.acmecustomer.models;

import org.feup.cmov.acmecustomer.interfaces.QRCodeInterface;

public class Customer implements QRCodeInterface {
    private CustomerMetadata metadata;
    private PaymentInfo paymentInfo;

    public Customer(String name, String username, String password, PaymentInfo paymentInfo) {
        this.metadata = new CustomerMetadata(name, username, password);
        this.paymentInfo = paymentInfo;
    }

    public String getName() {
        return this.metadata.getName();
    }

    public String getUsername() {
        return this.metadata.getUsername();
    }

    public String encode() {
        return "";
    }

}
