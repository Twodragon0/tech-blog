import {Composition} from 'remotion';
import {BlogVideo} from './BlogVideo';
import './index.css';

// 동적 props를 위한 타입 정의
interface VideoConfig {
	title: string;
	thumbnail: string;
	audioPath: string;
	segments?: Array<{
		text: string;
		startTime: number;
		duration: number;
		image?: string;
	}>;
	durationInFrames: number;
}

// 설정 파일에서 읽기
const getVideoConfig = (): VideoConfig => {
	try {
		// public/video-config.json에서 설정 읽기
		const config = require('../public/video-config.json');
		return config;
	} catch (e) {
		// 기본값 사용 (설정 파일이 없을 경우)
		return {
			title: 'Blog Post Title',
			thumbnail: 'default-thumbnail.png',
			audioPath: 'audio.mp3',
			segments: [],
			durationInFrames: 300, // 10초 (30fps 기준)
		};
	}
};

export const RemotionRoot: React.FC = () => {
	const config = getVideoConfig();

	return (
		<>
			<Composition
				id="BlogVideo"
				component={BlogVideo}
				durationInFrames={config.durationInFrames}
				fps={30}
				width={1920}
				height={1080}
				defaultProps={{
					title: config.title,
					thumbnail: config.thumbnail,
					audioPath: config.audioPath,
					segments: config.segments || [],
				}}
			/>
		</>
	);
};
