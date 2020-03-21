# smart-farm-device

**1. 개요**
- 스마트 화분 키트 하드웨어 제어 코드입니다
- 아직 실제로 물을 채우거나 흙을 채워서 테스트해보지 않아서 해당 부분 검증이 필요합니다


**2. 코드 자동실행**

해당 코드가 라즈베리파이 부팅될 때 자동으로 실행되도록 하려면 다음과 같이 설정을 진행하면 됩니다

(참고: https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/)
1. autostart 스크립트 수정
```
sudo nano /etc/rc.local                       # /etc/rc.local 스크립트 열기(nano editor 이용)
@sudo python3 /home/pi/*[FILE_PATH]*/app.py   # 해당 스크립트에 이 코드를 추가
```

2. 해당 스크립트 저장 후 종료
`control + x`(nano editor 저장&종료 키)

3. 재부팅
```
sudo reboot
```

4. 코드 자동실행 잘 되는지 확인
```
ps -ef | grep app.py
```
