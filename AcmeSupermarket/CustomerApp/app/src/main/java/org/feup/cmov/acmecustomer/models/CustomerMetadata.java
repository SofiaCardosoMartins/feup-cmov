package org.feup.cmov.acmecustomer.models;

import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;

import java.io.Serializable;
import java.math.BigInteger;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.spec.AlgorithmParameterSpec;
import java.util.Calendar;
import java.util.GregorianCalendar;

import javax.security.auth.x500.X500Principal;

public class CustomerMetadata implements Serializable {
    private String name;
    private String username;
    private String password;
    private transient KeyPair keyPair;

    protected CustomerMetadata(String name, String username, String password) {
        this.name = name;
        this.username = username;
        this.password = password;
        this.generateKeyPair();
    }

    private void generateKeyPair() {
        final String ANDROID_KEYSTORE = "AndroidKeyStore";
        final int KEY_SIZE = 512;
        final String KEY_ALGO = "RSA";
        final int CERT_SERIAL = 12121212;
        //final String ENC_ALGO = "RSA/NONE/PKCS1Padding";
        String keyName = "AcmeKey";

        try {
            Calendar start = new GregorianCalendar();
            Calendar end = new GregorianCalendar();
            end.add(Calendar.YEAR, 20);
            KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance(KEY_ALGO, ANDROID_KEYSTORE);
            AlgorithmParameterSpec spec = new KeyGenParameterSpec.Builder(keyName, KeyProperties.PURPOSE_SIGN | KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
                    .setKeySize(KEY_SIZE)
                    .setCertificateSubject(new X500Principal("CN=" + keyName))
                    .setCertificateSerialNumber(BigInteger.valueOf(CERT_SERIAL))
                    .setCertificateNotBefore(start.getTime())
                    .setCertificateNotAfter(end.getTime())
                    .build();
            keyPairGenerator.initialize(spec);
            this.keyPair = keyPairGenerator.generateKeyPair();
        } catch(Exception e) {
            e.printStackTrace();
        }
    }

    protected String getName() {
        return this.name;
    }

    protected String getUsername() {
        return this.username;
    }

    protected String getPassword() {
        return this.password;
    }

    public KeyPair getKeyPair() {
        return this.keyPair;
    }
}
